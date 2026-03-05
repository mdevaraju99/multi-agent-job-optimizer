# Mode Comparison: POC vs Industry

Both modes use the **exact same optimization logic**, agents, and constraints. The only difference is the data input method.

---

## Common Features (Both Modes)

### ✅ Optimization Agents
- **Baseline (FCFS)**: First-Come-First-Served with Rush priority
- **Batching (AI)**: Groups jobs by pharmaceutical product to minimize setup/cleaning
- **Bottleneck (AI)**: Balances workload across production lines
- **Orchestrated**: Multi-agent collaboration to select best strategy
- **Compare All**: Run all agents and compare results

### ✅ Constraint Validation
All agents enforce the same constraints:
1. Machine compatibility (jobs only run on compatible machines)
2. Shift boundaries (default 08:00 - 16:00)
3. Rush job deadlines (CRITICAL priority)
4. Downtime conflicts (jobs cannot overlap with maintenance)
5. Time overlaps (no job overlaps on same machine)
6. Job assignment (all jobs must be scheduled)

### ✅ KPI Metrics
- **Score**: Overall performance (0-100)
- **Makespan**: Total production time
- **Setup Time**: Equipment changeover time
- **Tardiness**: Late job penalties
- **Product Switches**: Number of product changes
- **Load Balance Variance**: Workload distribution quality
- **Bottleneck Machine**: Most heavily loaded machine

### ✅ Features
- Gantt chart visualization (color-coded by pharmaceutical product)
- AI explanations (pharmaceutical production context)
- Constraint violation reports
- Job allocation tables
- Manual downtime simulation (click "Simulate Failure" in both modes)
- Dynamic machine count support
- Rush job prioritization

---

## POC Mode (Proof of Concept)

### 🎯 Purpose
Quick testing and demonstration with randomly generated data.

### 📊 Data Input
**Random Generation:**
- **Job Count**: Specify number of jobs (default: 20)
- **Machine Count**: Specify number of machines (default: 4)
- **Rush Order %**: Percentage of jobs marked as Rush (default: 20%)
- Click **"Generate Input Data"** to create random pharmaceutical production jobs

**Downtime:**
- **Count**: Number of random downtime events
- Click **"Generate Random Downtime"** to add equipment failures/maintenance

**Manual Simulation:**
- Click **"Simulate Failure"** to open modal
- Specify machine, time range, and reason manually

### 🔧 Products Generated
Random jobs use pharma products:
- Paracetamol_500mg
- Ibuprofen_400mg
- Amoxicillin_250mg
- Aspirin_75mg
- Metformin_500mg

---

## Industry Mode (Production)

### 🎯 Purpose
Real-world deployment with actual production data from CSV files.

### 📊 Data Input
**CSV Upload:**
- **Jobs**: Upload CSV file with job details
- **Downtime**: Upload CSV file with scheduled maintenance/failures

**Manual Simulation:**
- Click **"Simulate Failure"** to add ad-hoc downtime (same as POC mode)

### 📄 CSV Formats

#### Jobs CSV (Required Columns):
```csv
job_id,product_type,machine_options,processing_time,priority,due_time
J001,Paracetamol_500mg,M1;M2;M4,45,Rush,11:30
J002,Ibuprofen_400mg,M1;M3,60,Normal,12:00
```

**Columns:**
- `job_id`: Unique identifier (e.g., J001)
- `product_type`: Product name (e.g., Paracetamol_500mg)
- `machine_options`: Semicolon-separated machine IDs (e.g., M1;M2;M4)
- `processing_time`: Duration in minutes (integer)
- `priority`: "Rush" or "Normal" (optional, default: Normal)
- `due_time`: Deadline in HH:MM format (optional)

#### Downtime CSV (Required Columns):
```csv
machine_id,start_time,end_time,reason
M2,10:30,11:00,Equipment Cleaning
M3,13:00,13:45,Quality Calibration
```

**Columns:**
- `machine_id`: Machine identifier (e.g., M1, M2)
- `start_time`: Start time in HH:MM format
- `end_time`: End time in HH:MM format
- `reason`: Description (optional, default: "Maintenance")

### 📦 Sample Files
See `sample_jobs.csv` and `sample_downtime.csv` for examples.

---

## Workflow Comparison

### POC Mode Workflow:
1. Set job count, machine count, rush percentage
2. Click "Generate Input Data"
3. (Optional) Generate random downtime
4. Select optimization agent
5. View results

### Industry Mode Workflow:
1. Prepare CSV files with actual production data
2. Upload Jobs CSV
3. Upload Downtime CSV (if applicable)
4. (Optional) Add manual downtime via "Simulate Failure"
5. Select optimization agent
6. View results

---

## Key Points

1. **Same optimization algorithms** - no difference in how agents work
2. **Same validation** - constraints enforced identically
3. **Same features** - all capabilities available in both modes
4. **Only difference** - data input method (random vs. CSV upload)
5. **Manual downtime** - "Simulate Failure" button works in both modes

Both modes are production-ready for pharmaceutical manufacturing optimization!
