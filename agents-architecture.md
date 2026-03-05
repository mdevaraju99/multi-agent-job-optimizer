# Multi-Agent Production Job Optimizer - Architecture & Rules Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Agent Roles & Responsibilities](#agent-roles--responsibilities)
4. [Rules & Constraints](#rules--constraints)
5. [Workflow Pipeline](#workflow-pipeline)
6. [How Agents Work Together](#how-agents-work-together)
7. [Baseline Scheduler](#baseline-scheduler)

---

## 🎯 Overview

This project implements a **Multi-Agent AI Production Scheduling System** that optimizes job scheduling on manufacturing machines. The system uses **LangGraph** for orchestration and **Groq's LLMs** (llama-3.3-70b-versatile) for intelligent decision-making.

### Key Technologies:
- **Framework**: LangGraph for multi-agent coordination
- **LLM**: Groq API with llama-3.3-70b-versatile model
- **Language**: Python 3.x
- **State Management**: TypedDict-based state passing
- **Tracing**: LangSmith for full observability

---

## 🏗️ System Architecture

The system consists of **5 specialized agents** working in a coordinated pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (LangGraph)                  │
│  Coordinates workflow, manages state, handles retries       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      SUPERVISOR AGENT (Coordinator)      │
        │  • Analyzes requests                     │
        │  • Selects best schedule                 │
        │  • Generates explanations                │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────┐                    ┌──────────────────────┐
│ BATCHING AGENT   │                    │ BOTTLENECK AGENT     │
│ (Setup Min.)     │                    │ (Load Balancing)     │
└──────────────────┘                    └──────────────────────┘
        │                                            │
        └─────────────────────┬──────────────────────┘
                              ▼
                ┌──────────────────────────┐
                │  CONSTRAINT AGENT        │
                │  (Validation)            │
                └──────────────────────────┘
```

---

## 👥 Agent Roles & Responsibilities

### 1. **Supervisor Agent** 🎯
**File**: `agents/supervisor.py`  
**Model**: llama-3.3-70b-versatile (most powerful)  
**Type**: LLM-Powered (Temperature: 0.2)

#### Responsibilities:
- **Analyzes optimization requests** and identifies key challenges
- **Coordinates** all specialist agents
- **Evaluates** candidate schedules using weighted KPIs
- **Selects** the best schedule from multiple candidates
- **Generates** executive-level explanations for managers

#### Rules Set in Supervisor:
```python
System Prompt Rules:
1. Coordinate specialist agents (Batching, Bottleneck, Constraint)
2. Evaluate schedules based on:
   - Total tardiness (meeting deadlines)
   - Setup time and number of switches
   - Machine utilization balance
   - Constraint violations (MUST be zero)
   - Rush job priority
3. Make final selection decisions
4. Generate clear, non-technical explanations for plant managers
```

#### Decision Logic:
- Scores each candidate schedule using **weighted KPI formula**
- Lower score = better schedule
- Prioritizes schedules with:
  - ✅ Zero constraint violations
  - ✅ Minimum total tardiness
  - ✅ Balanced machine utilization
  - ✅ Fewer setup transitions

---

### 2. **Batching Agent** 🔄
**File**: `agents/batching_agent.py`  
**Model**: llama-3.3-70b-versatile  
**Type**: LLM-Powered (Temperature: 0.1)

#### Responsibilities:
- **Groups jobs by product type** to minimize setup changes
- **Suggests optimal job sequences** that reduce changeover time
- **Minimizes setup transitions** between different product types
- **Balances** batching efficiency with meeting deadlines

#### Rules Set in Batching Agent:
```python
IMPORTANT RULES (from system_prompt):
1. Group jobs by product type to minimize setup changes
2. Suggest optimal job sequences that reduce setup time
3. Balance between batching efficiency and meeting deadlines
4. Rush jobs (priority='rush') MUST be prioritized even if they break batching
5. Consider setup times between product types
6. Aim to minimize total setup time while respecting priorities
```

#### Scheduling Algorithm:
```python
Step 1: Group jobs by product_type
        product_groups = defaultdict(list)
        for job in jobs:
            product_groups[job.product_type].append(job)

Step 2: Within each product group, prioritize rush jobs
        for product_type in product_groups:
            product_groups[product_type].sort(
                key=lambda j: (0 if j.is_rush else 1, j.due_time)
            )

Step 3: Distribute product groups across machines to balance load
        - Sort machines by current load (least loaded first)
        - Assign jobs to compatible machines
        - Track current_product on each machine

Step 4: Calculate setup time
        if prev_product != current_product:
            setup_time = constraint.get_setup_time(prev_product, current_product)
        else:
            setup_time = constraint.get_setup_time(product, product) # Same product

Step 5: SKIP DOWNTIME WINDOWS
        - Try up to 20 slot search attempts
        - If downtime conflict detected, skip past it
        - Find next available slot after downtime
```

#### Key Features:
- ✅ Batches similar products together
- ✅ Minimizes expensive setup transitions (e.g., P_A→P_B costs 30 min)
- ✅ Rush jobs always get priority within their product batch
- ✅ Automatically avoids machine downtime windows

---

### 3. **Bottleneck Agent** ⚖️
**File**: `agents/bottleneck_agent.py`  
**Model**: llama-3.3-70b-versatile  
**Type**: LLM-Powered (Temperature: 0.1)

#### Responsibilities:
- **Detects machines with excessive load** or long queues
- **Identifies underutilized machines**
- **Re-routes compatible jobs** to balance workload
- **Improves overall utilization balance** and reduces makespan

#### Rules Set in Bottleneck Agent:
```python
IMPORTANT RULES (from system_prompt):
1. Detect overloaded machines (bottlenecks)
2. Find underutilized machines
3. Suggest job redistributions to balance the load
4. Ensure job-machine compatibility when moving jobs
5. Prioritize balancing utilization across all machines
6. Consider both processing time and downtime
```

#### Rebalancing Algorithm:
```python
Step 1: Calculate current loads per machine
        machine_loads = {m.machine_id: total_processing_time for m in machines}

Step 2: Identify bottleneck and underutilized machines
        max_load = max(machine_loads.values())
        min_load = min(machine_loads.values())
        imbalance = max_load - min_load

Step 3: Sort jobs by priority (rush first, then deadline)
        remaining_jobs.sort(
            key=lambda j: (0 if j.is_rush else 1, j.due_time)
        )

Step 4: Assign jobs using LOAD-BALANCING strategy
        - Find compatible machines for each job
        - Sort by current load (LOWEST FIRST)
        - Assign to least-loaded compatible machine
        - Update tracking: current_loads[machine_id] += job_time + setup_time

Step 5: Calculate improvement
        new_imbalance = new_max_load - new_min_load
        improvement = old_imbalance - new_imbalance
```

#### Key Features:
- ✅ Balances workload across all machines
- ✅ Reduces makespan (total completion time)
- ✅ Preserves rush job priority
- ✅ Only moves jobs to compatible machines
- ✅ Avoids downtime windows during rebalancing

---

### 4. **Constraint Agent** ✅
**File**: `agents/constraint_agent.py`  
**Type**: **Deterministic Rule-Based** (NO LLM)  
**Reason**: Reliability - constraints must be checked deterministically

#### Responsibilities:
- **Validates** schedules against all operational constraints
- **Checks** shift boundary compliance
- **Detects** machine downtime conflicts
- **Enforces** rush order priority rules
- **Verifies** setup time constraints
- **Returns** violation reports or approval

#### Rules Set in Constraint Agent:
```python
COMPREHENSIVE VALIDATION CHECKS:

1. JOB ASSIGNMENT CHECK
   - Ensure all jobs are assigned to machines
   - No jobs left unscheduled

2. SHIFT BOUNDARY CHECK
   - Job end_time <= shift_end + max_overtime_minutes
   - Example: Shift 08:00-17:00 + 60min overtime = 18:00 max

3. MACHINE COMPATIBILITY CHECK
   - Machine can produce the job's product_type
   - machine.can_produce(job.product_type) == True

4. DOWNTIME CONFLICT CHECK
   - Job must NOT overlap with machine downtime
   - Check all downtime windows for each machine
   - If overlap detected → VIOLATION

5. TIME OVERLAP CHECK (Same Machine)
   - No two jobs can run simultaneously on same machine
   - Check: end_time_job1 <= start_time_job2 OR end_time_job2 <= start_time_job1

6. RUSH JOB DEADLINE CHECK (CRITICAL)
   - All rush jobs MUST meet their deadlines
   - If rush job is late → CRITICAL VIOLATION
   - Calculate tardiness: end_time - due_time
```

#### Validation Output:
```python
Returns: Tuple[is_valid: bool, violations: List[str], report: str]

If VALID:
    ✓ All jobs assigned
    ✓ Shift boundaries respected
    ✓ No downtime conflicts
    ✓ Machine compatibility verified
    ✓ No time overlaps
    ✓ Rush deadlines met

If INVALID:
    ✗ List of specific violations
    ✗ CANNOT execute schedule
    ✗ Must retry optimization
```

#### Key Features:
- ✅ **100% Deterministic** - no AI unpredictability
- ✅ **Comprehensive** - checks all constraint types
- ✅ **Fast** - rule-based checking is instant
- ✅ **Detailed reporting** - explains each violation

---

### 5. **Orchestrator (LangGraph)** 🚀
**File**: `agents/orchestrator.py`  
**Type**: Workflow Coordinator (uses LangGraph StateGraph)

#### Responsibilities:
- **Builds** the LangGraph workflow pipeline
- **Manages state** passing between agents
- **Coordinates** agent execution order
- **Handles retries** if schedules fail validation
- **Tracks** optimization time and metadata

#### Workflow Pipeline:
```python
STEP-BY-STEP EXECUTION:

1. analyze_request (Supervisor)
   └─> Analyze jobs, machines, constraints
   
2. create_baseline_schedule (Baseline Scheduler)
   └─> Simple FIFO schedule for comparison
   
3. create_batching_schedule (Batching Agent)
   └─> Setup-optimized schedule
   
4. create_bottleneck_schedule (Bottleneck Agent)
   └─> Load-balanced schedule (starts from batching)
   
5. validate_schedules (Constraint Agent)
   └─> Validate all 3 candidates
   
6. select_best (Supervisor)
   └─> Choose best valid schedule
   └─> Return final schedule + explanation
```

#### State Management:
```python
class OptimizationState(TypedDict):
    # Inputs
    jobs: List[Job]
    machines: List[Machine]
    constraint: Constraint
    
    # Agent Results
    supervisor_analysis: str
    baseline_schedule: Schedule
    batching_schedule: Schedule
    bottleneck_schedule: Schedule
    
    # Validation Results
    baseline_valid: bool
    batching_valid: bool
    bottleneck_valid: bool
    baseline_violations: List[str]
    batching_violations: List[str]
    bottleneck_violations: List[str]
    
    # Final Output
    final_schedule: Schedule
    final_explanation: str
    status: str  # "running", "completed", "best-effort", "failed"
```

#### Best-Effort Fallback:
If NO schedule is fully valid, orchestrator uses **best-effort approach**:
```python
1. Select schedule with FEWEST violations
2. Mark status as "best-effort"
3. Include warning in explanation
4. Suggest improvements (extend shift, reduce jobs, etc.)
```

---

## 📏 Rules & Constraints

### Global Constraints (Applied by All Agents)

#### 1. **Shift Boundaries**
```python
constraint.shift_start = time(8, 0)   # 8:00 AM
constraint.shift_end = time(17, 0)     # 5:00 PM
constraint.max_overtime_minutes = 60   # Max 1 hour overtime

RULE: job.end_time <= shift_end + max_overtime (18:00)
```

#### 2. **Setup Times** (Product Transitions)
```python
constraint.setup_times = {
    "P_A->P_A": 5,   # Same product: 5 min
    "P_A->P_B": 30,  # Different product: 30 min
    "P_B->P_A": 30,
    "P_B->P_B": 5,
    # etc...
}

RULE: When changing products, add setup_time before next job
```

#### 3. **Machine Downtime**
```python
machine.downtime_windows = [
    DowntimeWindow(time(10, 0), time(11, 0), "Maintenance"),
    DowntimeWindow(time(14, 0), time(14, 30), "Quality Check")
]

RULE: Jobs CANNOT overlap with downtime windows
      If conflict detected, skip past downtime window
```

#### 4. **Rush Job Priority**
```python
job.priority = "rush"  # or "normal"
job.is_rush = True

RULES:
1. Rush jobs ALWAYS prioritized over normal jobs
2. Rush jobs MUST meet their deadlines
3. If rush job late → CRITICAL VIOLATION
4. Sort order: (0 if rush else 1, due_time)
```

#### 5. **Machine Capabilities**
```python
machine.capabilities = ["P_A", "P_B"]  # Can produce P_A and P_B
job.product_type = "P_A"

RULE: Job can only be assigned to compatible machines
      machine.can_produce(job.product_type) must be True
```

#### 6. **Job-Machine Compatibility**
```python
job.compatible_machines = ["M1", "M2"]  # Job can run on M1 or M2

RULE: Job can only be assigned to machines in its compatible_machines list
      job.can_run_on(machine_id) must be True
```

---

## 🔄 Workflow Pipeline

### Complete Execution Flow:

```
START
  │
  ▼
┌─────────────────────────────────────┐
│ 1. SUPERVISOR ANALYSIS              │
│    • Analyze request                │
│    • Identify challenges            │
│    • Create strategy                │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│ 2. BASELINE SCHEDULE (Comparison)   │
│    • Simple FIFO algorithm          │
│    • No optimization                │
│    • Shows improvement baseline     │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│ 3. BATCHING AGENT                   │
│    • Group by product type          │
│    • Minimize setup transitions     │
│    • Prioritize rush jobs           │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│ 4. BOTTLENECK AGENT                 │
│    • Start from batching schedule   │
│    • Rebalance machine loads        │
│    • Reduce makespan                │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│ 5. CONSTRAINT VALIDATION            │
│    • Validate baseline schedule     │
│    • Validate batching schedule     │
│    • Validate bottleneck schedule   │
│    • Report violations              │
└─────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────┐
│ 6. SUPERVISOR SELECTION             │
│    • Collect valid candidates       │
│    • Score using weighted KPIs      │
│    • Select best schedule           │
│    • Generate explanation           │
└─────────────────────────────────────┘
  │
  ▼
END (Return Final Schedule)
```

---

## 🤝 How Agents Work Together

### Collaboration Pattern:

#### **Sequential Pipeline with Validation Gates**

```
Batching Agent → Bottleneck Agent → Constraint Agent → Supervisor
     ↓                  ↓                    ↓              ↓
 Schedule A         Schedule B          Validation      Selection
 (Setup Min)        (Load Bal.)        (Pass/Fail)    (Best KPIs)
```

### Example Scenario:

**Input**: 10 jobs, 3 machines, rush orders, downtime windows

**Step 1 - Supervisor**:
- Analyzes: "5 rush jobs, 2 product types (P_A, P_B), Machine M2 has 1hr downtime"
- Strategy: "Prioritize rush jobs, minimize P_A↔P_B transitions, balance load"

**Step 2 - Baseline**:
- FIFO: Assigns jobs in order
- No optimization
- Result: 120 min tardiness, 6 setup switches

**Step 3 - Batching Agent**:
- Groups: [P_A, P_A, P_A] then [P_B, P_B, P_B]
- Prioritizes rush jobs within each group
- Result: 80 min tardiness, 3 setup switches (50% reduction!)
- Avoids downtime windows

**Step 4 - Bottleneck Agent**:
- Analyzes load: M1=180min, M2=60min, M3=150min
- Rebalances: Move some M1 jobs to M2 (underutilized)
- Result: 70 min tardiness, 4 setup switches, balanced utilization

**Step 5 - Constraint Agent**:
- Validates baseline: ❌ 2 violations (downtime conflict, rush job late)
- Validates batching: ✅ VALID
- Validates bottleneck: ✅ VALID

**Step 6 - Supervisor**:
- Scores batching: 85.0 points
- Scores bottleneck: 78.0 points (LOWER IS BETTER)
- **Selects bottleneck schedule** (best balance of all KPIs)
- Explanation: "Selected for superior load balancing while maintaining low tardiness"

---

## 📊 Baseline Scheduler

### Purpose:
**Comparison Baseline** - Shows improvement achieved by AI optimizer

**File**: `utils/baseline_scheduler.py`  
**Type**: Simple deterministic algorithm (NO AI)

### Algorithm:
```python
FIFO (First-In-First-Out) with Minimal Intelligence

Step 1: Sort jobs
        - Rush jobs first
        - Then by job_id (arrival order)

Step 2: For each job:
        - Find compatible machines
        - Try FIRST compatible machine
        - Find earliest available time slot
        - If downtime conflict, skip past it
        - Assign job

Step 3: No optimization:
        ❌ No batching
        ❌ No load balancing
        ❌ No setup optimization
        ❌ No intelligent machine selection
```

### Key Characteristics:
- ✅ Simple and predictable
- ✅ Fast execution
- ✅ Respects constraints
- ❌ Poor KPI performance
- ❌ High setup time
- ❌ Imbalanced machine utilization
- ❌ High tardiness

### Comparison Use:
The AI optimizer should show:
- **40-60% reduction** in total tardiness
- **30-50% reduction** in setup transitions
- **Better load balance** across machines
- **Fewer constraint violations**

---

## 🎯 Key Performance Indicators (KPIs)

### Weighted Scoring Formula:
```python
score = (
    total_tardiness * weight_tardiness +
    total_setup_time * weight_setup +
    num_setup_switches * weight_switches +
    utilization_imbalance * weight_balance +
    num_violations * weight_violations  # Usually infinite penalty
)

Default Weights:
- tardiness: 2.0 (most important - customer satisfaction)
- setup_time: 1.0
- setup_switches: 5.0 (expensive)
- utilization_imbalance: 1.5
- violations: 1000.0 (must be zero)
```

### KPI Definitions:

#### 1. **Total Tardiness**
```python
Sum of all late jobs' delay times
tardiness = max(0, job.end_time - job.due_time)
```

#### 2. **Total Setup Time**
```python
Sum of all setup times across all jobs
Includes product transitions on each machine
```

#### 3. **Number of Setup Switches**
```python
Count of product type changes
P_A → P_B counts as 1 switch
```

#### 4. **Utilization Imbalance**
```python
Difference between most loaded and least loaded machine
imbalance = max_utilization - min_utilization
```

#### 5. **Constraint Violations**
```python
Count of any constraint violations
MUST BE ZERO for valid schedule
```

---

## 🔍 LangSmith Tracing

All agent actions are traced using **@traceable** decorator:

```python
@traceable(name="Batching Agent Schedule")
def _create_batching_schedule(self, state):
    # ... agent logic ...
    return state
```

### Benefits:
- ✅ Full visibility into agent decisions
- ✅ Debug LLM prompts and responses
- ✅ Track execution time per agent
- ✅ Replay failed optimization runs
- ✅ Monitor token usage and costs

---

## 🚀 Example Execution

```python
from agents.orchestrator import OptimizationOrchestrator

# Initialize
orchestrator = OptimizationOrchestrator()

# Run optimization
result = orchestrator.optimize(
    jobs=job_list,
    machines=machine_list,
    constraint=constraint_obj
)

# Get results
if result["success"]:
    schedule = result["schedule"]
    print(result["explanation"])
    
    # Access KPIs
    print(f"Tardiness: {schedule.kpis.total_tardiness} min")
    print(f"Setup Time: {schedule.kpis.total_setup_time} min")
    print(f"Utilization Balance: {schedule.kpis.utilization_imbalance:.1f}%")
```

---

## 📝 Summary

### Agent Hierarchy:
```
ORCHESTRATOR (LangGraph)
├── SUPERVISOR (Coordinator & Decision Maker)
├── BATCHING AGENT (Setup Optimization)
├── BOTTLENECK AGENT (Load Balancing)
└── CONSTRAINT AGENT (Validation)
```

### Rule Enforcement:
- **Batching Agent**: Minimize setup, respect rush priority
- **Bottleneck Agent**: Balance load, preserve compatibility
- **Constraint Agent**: Validate ALL constraints deterministically
- **Supervisor**: Select best based on weighted KPIs

### Success Criteria:
1. ✅ All jobs assigned
2. ✅ All constraints satisfied
3. ✅ Rush jobs meet deadlines
4. ✅ No downtime conflicts
5. ✅ Optimal KPI score

---

**End of Document** - Generated for Job Optimizer Project
