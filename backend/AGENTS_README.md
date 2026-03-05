# Multi-Agent Production Job Optimizer - Complete Implementation Guide

## 🎯 Project Overview

This project implements a **dual-architecture multi-agent optimization system** for production job scheduling:

1. **Simplified Agents** (Current) - Uses Pydantic schemas, faster, API-ready
2. **Comprehensive LangGraph Agents** (Advanced) - Full LangGraph workflow, LangSmith tracing

Both systems work together and can be used independently or in combination.

---

## 📁 Project Structure

```
backend/
├── models/
│   ├── schemas.py           # Pydantic models (simplified API)
│   ├── job.py               # Class-based Job model
│   ├── machine.py           # Machine, Constraint, DowntimeWindow models
│   └── schedule.py          # Schedule, JobAssignment, KPI models
│
├── agents/
│   ├── base_agent.py        # Base agent class (simplified)
│   ├── baseline_agent.py    # FIFO baseline (simplified)
│   ├── batching_agent.py    # Setup minimization (simplified)
│   ├── bottleneck_agent.py  # Load balancing (simplified)
│   ├── constraint_agent.py  # Constraint validation (simplified)
│   ├── orchestrator.py      # Orchestration (simplified)
│   └── supervisor.py        # Supervisor agent (LangGraph)
│
└── utils/
    ├── model_adapter.py     # Bridge between schema and class models
    ├── baseline_scheduler.py # Baseline FIFO scheduler (class-based)
    ├── config_loader.py     # Load machines and constraints
    ├── data_generator.py    # Generate random test jobs
    ├── kpi_calculator.py    # KPI calculation utilities
    └── csv_handler.py       # CSV import/export
```

---

## 🔄 Two Agent Systems Explained

### System 1: Simplified Agents (Current Production)

**Location:** `agents/baseline_agent.py`, `batching_agent.py`, `bottleneck_agent.py`

**Data Models:** Pydantic schemas (`models/schemas.py`)

**Features:**
- ✅ Fast async execution
- ✅ Direct API integration
- ✅ Lightweight Groq LLM calls
- ✅ Simple orchestration

**Use Cases:**
- Production API endpoints
- Quick optimization requests
- Web dashboard integration

**Example:**
```python
from agents.batching_agent import BatchingAgent
from models.schemas import Job, ShiftConstraints

agent = BatchingAgent()
result = await agent.optimize(jobs, downtimes, constraints)
```

---

### System 2: Comprehensive LangGraph Agents (Advanced)

**Location:** `models/job.py`, `machine.py`, `schedule.py` + comprehensive agent files

**Data Models:** Class-based models with methods

**Features:**
- ✅ Full LangGraph state management
- ✅ LangSmith tracing and debugging
- ✅ Advanced KPI calculation
- ✅ Constraint validation with retry logic
- ✅ Multi-candidate comparison
- ✅ Detailed explanations

**Use Cases:**
- Research and development
- Complex optimization scenarios
- Detailed performance analysis
- LangSmith monitoring

**Example:**
```python
from agents.orchestrator import OptimizationOrchestrator
from utils.config_loader import load_config
from utils.data_generator import generate_random_jobs

orchestrator = OptimizationOrchestrator()
config = load_config()
jobs = generate_random_jobs(15)

result = orchestrator.optimize(
    jobs=jobs,
    machines=config['machines'],
    constraint=config['constraint']
)
```

---

## 🌉 Using the Model Adapter

The `ModelAdapter` bridges both systems, allowing you to:
- Convert Pydantic jobs to class-based jobs
- Use LangGraph agents with API data
- Get results in either format

```python
from utils.model_adapter import ModelAdapter

# Convert schema job to class-based job
job = ModelAdapter.schema_job_to_job(schema_job)

# Convert downtimes to machines
machines = ModelAdapter.downtimes_to_machines(downtimes)

# Convert schedule to API result
result = ModelAdapter.schedule_to_schema_result(
    schedule, "Advanced Agent", jobs, machines, constraint
)
```

---

## 📊 Agent Capabilities Matrix

| Agent | Purpose | LLM Used | Optimization Strategy |
|-------|---------|----------|----------------------|
| **Baseline** | FIFO reference | None | Rush first, then due time |
| **Batching** | Setup minimization | Llama-3.1-8b-instant | Group by product type |
| **Bottleneck** | Load balancing | Llama-3.1-8b-instant | Distribute to least-loaded |
| **Constraint** | Validation | None (rule-based) | Check all constraints |
| **Supervisor** | Final selection | Llama-3.3-70b | KPI-weighted scoring |
| **Orchestrator** | Workflow coordination | Llama-3.3-70b | LangGraph state machine |

---

## 🚀 Execution Guide

### Option 1: Use Simplified Agents (Current API)

Already implemented in your routes:

```bash
# Start backend
cd backend
python main.py

# Test API
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

---

### Option 2: Use LangGraph Orchestrator (Advanced)

#### Step 1: Configure Environment

Ensure `.env` has:
```
GROQ_API_KEY=your_groq_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=multi-agent-job-optimizer
LANGCHAIN_TRACING_V2=true
```

#### Step 2: Run Orchestrator

```python
# test_orchestrator.py
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import OptimizationOrchestrator
from utils.config_loader import load_config
from utils.data_generator import generate_random_jobs

# Generate test jobs
jobs = generate_random_jobs(15, rush_probability=0.25)

# Load configuration
config = load_config()

# Create orchestrator
orchestrator = OptimizationOrchestrator()

# Run optimization
result = orchestrator.optimize(
    jobs=jobs,
    machines=config['machines'],
    constraint=config['constraint']
)

# Print results
if result["success"]:
    print(result["explanation"])
    schedule = result["schedule"]
    print(f"\nScheduled: {len(schedule.get_all_jobs())} jobs")
else:
    print("Optimization failed!")
```

---

## 🔧 Implementation Rules (As Requested)

Based on the comprehensive agent code you provided, here are the **key implementation rules**:

### 1. **Proxy Environment Variable Removal**
All agents MUST remove proxy variables to avoid httpx errors:
```python
for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    if var in os.environ:
        del os.environ[var]
```

### 2. **Downtime Window Handling**
Agents MUST skip downtime windows when scheduling:
```python
# Check downtime conflicts
for downtime in machine.downtime_windows:
    if downtime.overlaps_with(proposed_start, proposed_end, date_context=now):
        # Skip past the downtime and search again
        search_start_time = downtime.end_time
```

### 3. **Rush Job Priority**
Rush jobs MUST be prioritized:
```python
jobs.sort(key=lambda j: (0 if j.is_rush else 1, j.due_time))
```

### 4. **Setup Time Calculation**
Setup times depend on product transitions:
```python
if prev_product and prev_product != job.product_type:
    setup_time = constraint.get_setup_time(prev_product, job.product_type)
elif prev_product == job.product_type:
    setup_time = constraint.get_setup_time(job.product_type, job.product_type)
else:
    setup_time = 0
```

### 5. **Shift Boundary Enforcement**
Jobs MUST fit within shift + overtime:
```python
shift_end_min = (
    constraint.shift_end.hour * 60 + 
    constraint.shift_end.minute + 
    constraint.max_overtime_minutes
)
if end_min > shift_end_min:
    continue  # Skip job
```

### 6. **KPI-Based Schedule Selection**
Supervisor selects schedule with best weighted score:
```python
score = (
    kpis.total_tardiness * weights["tardiness"] +
    kpis.total_setup_time * weights["setup_time"] +
    kpis.utilization_imbalance * weights["utilization"] +
    kpis.num_violations * 1000
)
```

### 7. **Constraint Validation**
All schedules MUST pass constraint validation:
```python
is_valid, violations, report = constraint_agent.validate_schedule(
    schedule, jobs, machines, constraint
)
if not is_valid:
    # Retry or use best-effort
```

### 8. **LangGraph State Management**
Use TypedDict for state:
```python
class OptimizationState(TypedDict):
    jobs: List[Job]
    machines: List[Machine]
    constraint: Constraint
    # ... intermediate and final results
```

### 9. **LangSmith Tracing**
Decorate key methods:
```python
@traceable(name="Supervisor Analysis")
def _analyze_request(self, state: OptimizationState):
    # Agent logic here
```

### 10. **Best-Effort Fallback**
If no valid schedule exists, select one with fewest violations:
```python
if not valid_candidates:
    # Sort by violation count
    best_effort.sort(key=lambda x: x[2])
    return best_effort[0]
```

---

## 📈 Next Steps

1. **Test Both Systems** - Verify simplified and LangGraph agents work
2. **Integrate Adapter** - Use ModelAdapter in API routes
3. **Monitor with LangSmith** - Track agent performance
4. **Tune Weights** - Adjust KPI weights in constraints
5. **Add More Machines** - Extend machine configurations
6. **Custom Constraints** - Add industry-specific rules

---

## 🐛 Troubleshooting

### Issue: httpx proxy error
**Solution:** Agents remove proxy variables (already implemented)

### Issue: Jobs not fitting in shift
**Solution:** Increase `max_overtime_minutes` or reduce job count

### Issue: No valid schedule found
**Solution:** System uses best-effort with violation warnings

### Issue: LangSmith not tracing
**Solution:** Check `LANGCHAIN_TRACING_V2=true` and API key

---

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [LangSmith Platform](https://smith.langchain.com/)
- [Groq API](https://console.groq.com/)

---

**Status:** ✅ All agent rules implemented and ready for execution
