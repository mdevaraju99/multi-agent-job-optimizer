# 🤖 Multi-Agent Job Optimizer

<div align="center">

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![React](https://img.shields.io/badge/React-19.2-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-purple.svg)

**An AI-powered production scheduling system using multi-agent collaboration to optimize job allocation across manufacturing machines.**

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Agent Modes](#agent-modes)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## 🎯 Overview

The **Multi-Agent Job Optimizer** is an intelligent production scheduling system that uses AI agents to optimize job allocation across manufacturing machines. It considers multiple constraints including:

- ⏰ **Shift schedules** and overtime limits
- 🔧 **Setup times** for product transitions
- 🚨 **Downtime windows** for maintenance
- ⚡ **Rush orders** and due dates
- 🎨 **Product compatibility** across machines
- 📊 **Load balancing** and utilization optimization

The system employs multiple specialized agents that work together to find optimal schedules while respecting all operational constraints.

---

## ✨ Features

### 🤖 Multi-Agent Intelligence
- **Baseline Agent**: FIFO (First-In-First-Out) scheduling
- **Batching Agent**: Minimizes setup times by grouping similar products
- **Bottleneck Agent**: Balances workload across machines
- **Constraint Agent**: Validates schedules against all constraints
- **Supervisor Agent**: Coordinates agents and selects best solutions

### 📊 Advanced Scheduling
- Dual-mode operation (Simplified API & Comprehensive LangGraph)
- Rush order prioritization
- Dynamic setup time calculation
- Shift boundary enforcement
- Downtime window avoidance
- Multi-objective optimization (tardiness, setup time, utilization)

### 🎨 Interactive Dashboard
- Real-time Gantt chart visualization
- KPI comparison tables
- Constraint violation reports
- Job allocation analytics
- Agent explanation panels
- Dark/Light theme support

### 📈 Performance Analytics
- Tardiness tracking
- Setup time minimization
- Machine utilization balancing
- Constraint violation detection
- Comparative analysis (baseline vs optimized)

---

## 🏗️ Architecture

The system uses a **multi-agent architecture** powered by LangGraph and LangChain:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (LangGraph)                  │
│         Coordinates workflow & manages state                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      SUPERVISOR AGENT (Coordinator)      │
        │  • Analyzes job requirements             │
        │  • Selects optimal schedule              │
        │  • Generates explanations                │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────┐                    ┌──────────────────────┐
│ BATCHING AGENT   │                    │ BOTTLENECK AGENT     │
│ (Setup Min.)     │                    │ (Load Balancing)     │
│                  │                    │                      │
│ • Groups similar │                    │ • Distributes load   │
│   products       │                    │ • Balances machines  │
│ • Reduces setup  │                    │ • Rush priority      │
└──────────────────┘                    └──────────────────────┘
        │                                            │
        └─────────────────────┬─────────────────────┘
                              ▼
                ┌──────────────────────────┐
                │   CONSTRAINT AGENT       │
                │   (Validation)           │
                │                          │
                │ • Validates schedules    │
                │ • Checks constraints     │
                │ • Reports violations     │
                └──────────────────────────┘
```

### Agent Responsibilities

| Agent | Purpose | Key Features |
|-------|---------|--------------|
| **Baseline** | Simple FIFO scheduling | Quick baseline comparison |
| **Batching** | Minimize setup times | Groups similar products, reduces transitions |
| **Bottleneck** | Balance machine load | Distributes jobs evenly, prioritizes rush orders |
| **Constraint** | Validate schedules | Checks shift limits, downtimes, compatibility |
| **Supervisor** | Coordinate & decide | Analyzes results, selects best schedule, explains |

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **LangChain** - LLM application framework
- **LangGraph** - Multi-agent workflow orchestration
- **Groq API** - High-performance LLM inference (llama-3.3-70b-versatile)
- **Pydantic** - Data validation and settings management
- **Pandas** - Data manipulation and analysis
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icon library

### AI/ML
- **LangSmith** - LLM application monitoring and tracing
- **Groq** - Fast LLM inference
- **LangChain-Groq** - Groq integration for LangChain

---

## 📦 Installation

### Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **Groq API Key** (get from [console.groq.com](https://console.groq.com/))

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd multi-agent-job-optimizer-main
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
# Copy the example below or create manually
```

Create `backend/.env`:

```env
# Required: Groq API Key for LLM access
GROQ_API_KEY=your_groq_api_key_here

# Optional: LangSmith for tracing (debugging/monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=multi-agent-job-optimizer
LANGCHAIN_TRACING_V2=true
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install npm dependencies
npm install
```

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/config.py`:

```python
class Settings:
    # API Keys (loaded from .env)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    
    # LLM Models
    MODEL_NAME = "llama-3.3-70b-versatile"  # High performance
    FAST_MODEL_NAME = "llama-3.1-8b-instant"  # Faster, simpler tasks
    
    # App Settings
    PROJECT_NAME = "Multi-Agent Job Optimizer"
    VERSION = "0.1.0"
    API_PREFIX = "/api"
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` for the backend API.

To change the API URL, edit `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

---

## 🚀 Usage

### Starting the Application

#### Terminal 1 - Backend Server

```bash
cd backend
python main.py
```

Backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Interactive API documentation)

#### Terminal 2 - Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will be available at:
- **App**: http://localhost:5173

### Using the Application

1. **Open the Dashboard**: Navigate to http://localhost:5173
2. **Select Mode**: Choose between Simplified or Comprehensive agent modes
3. **Input Jobs**: 
   - Manually add jobs or
   - Upload CSV file (see `sample_jobs.csv`)
4. **Configure Machines**: 
   - Set machine capabilities
   - Define constraints and shift schedules
5. **Add Downtime**: Schedule maintenance windows
6. **Run Optimization**: Click "Optimize Schedule"
7. **View Results**:
   - Interactive Gantt chart
   - KPI comparisons
   - Constraint reports
   - Agent explanations

### Sample Data

The project includes sample CSV files:
- `sample_jobs.csv` - Example job data
- `sample_downtime.csv` - Example maintenance windows

---

## 📚 API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Data Management
```
POST   /api/jobs              - Create new jobs
GET    /api/jobs              - List all jobs
POST   /api/jobs/upload       - Upload jobs CSV
POST   /api/downtime          - Add downtime windows
```

#### Optimization
```
POST   /api/optimize/simplified     - Run simplified agents
POST   /api/optimize/comprehensive  - Run LangGraph agents
```

#### Simulation
```
POST   /api/simulate/baseline       - Run baseline FIFO
POST   /api/simulate/compare        - Compare strategies
```

### Request Example

```bash
curl -X POST "http://localhost:8000/api/optimize/simplified" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "product_id": "A",
        "quantity": 100,
        "due_time": 480,
        "is_rush": false
      }
    ],
    "machines": [...],
    "constraint": {...}
  }'
```

---

## 🔄 Agent Modes

The system supports **two operation modes**:

### 1. Simplified Mode (Recommended)
- ✅ Faster execution
- ✅ API-ready with Pydantic schemas
- ✅ Direct agent coordination
- ✅ Production-ready
- 📍 Default for REST API

**Use Case**: Production environments, API integrations, quick optimizations

### 2. Comprehensive Mode (Advanced)
- 🔬 Full LangGraph workflow
- 🔍 LangSmith tracing and monitoring
- 🧠 Advanced LLM reasoning
- 📊 Detailed state management
- 🔄 Retry logic and error handling

**Use Case**: Research, complex scenarios, detailed analysis, debugging

### Switching Modes

In the frontend dashboard, use the **Mode Selection** page to toggle between modes.

Via API, use different endpoints:
- `/api/optimize/simplified`
- `/api/optimize/comprehensive`

---

## 📁 Project Structure

```
multi-agent-job-optimizer-main/
│
├── backend/                          # FastAPI backend
│   ├── agents/                       # Agent implementations
│   │   ├── base_agent.py            # Base agent class
│   │   ├── baseline_agent.py        # FIFO baseline
│   │   ├── batching_agent.py        # Setup minimization
│   │   ├── bottleneck_agent.py      # Load balancing
│   │   ├── constraint_agent.py      # Validation
│   │   └── orchestrator.py          # Coordination
│   │
│   ├── models/                       # Data models
│   │   ├── schemas.py               # Pydantic schemas
│   │   ├── job.py                   # Job class
│   │   ├── machine.py               # Machine & Constraint
│   │   └── schedule.py              # Schedule & KPI
│   │
│   ├── routes/                       # API routes
│   │   ├── data_routes.py           # Data management
│   │   ├── optimization_routes.py   # Optimization
│   │   └── simulation_routes.py     # Simulation
│   │
│   ├── utils/                        # Utilities
│   │   ├── baseline_scheduler.py    # FIFO scheduler
│   │   ├── config_loader.py         # Config loading
│   │   ├── csv_handler.py           # CSV import/export
│   │   ├── data_generator.py        # Test data generation
│   │   ├── kpi_calculator.py        # KPI calculations
│   │   └── model_adapter.py         # Schema↔Class bridge
│   │
│   ├── config.py                     # Configuration
│   ├── main.py                       # FastAPI app
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── control/             # Control panels
│   │   │   ├── input/               # Input forms
│   │   │   └── output/              # Results display
│   │   │
│   │   ├── pages/                   # Page components
│   │   │   ├── Dashboard.jsx        # Main dashboard
│   │   │   └── ModeSelection.jsx    # Mode selector
│   │   │
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   │
│   │   ├── App.jsx                  # Main app component
│   │   └── main.jsx                 # Entry point
│   │
│   ├── package.json                  # npm dependencies
│   └── vite.config.js               # Vite configuration
│
├── sample_jobs.csv                   # Sample job data
├── sample_downtime.csv               # Sample downtime data
├── agents-architecture.md            # Architecture docs
├── AGENTS_README.md                  # Agent implementation guide
├── IMPLEMENTATION_SUMMARY.md         # Implementation notes
├── MODE_COMPARISON.md                # Mode comparison guide
└── README.md                         # This file
```

---

## 🔍 Key Features Explained

### Rush Order Handling
Jobs marked as `is_rush: true` are automatically prioritized:
```python
jobs.sort(key=lambda j: (0 if j.is_rush else 1, j.due_time))
```

### Setup Time Optimization
The Batching Agent groups similar products to minimize setup times:
```python
# Groups same product types together
# Calculates transition setup times
# Minimizes total changeover time
```

### Downtime Avoidance
Jobs automatically avoid scheduled maintenance windows:
```python
if downtime.overlaps_with(start, end):
    # Reschedule after downtime window
    start = downtime.end_time
```

### Shift Boundary Enforcement
Jobs respect shift schedules plus allowed overtime:
```python
shift_end = shift_end_time + max_overtime
if job_end > shift_end:
    # Job rejected - won't fit in shift
```

### Multi-Objective Optimization
Schedules are scored on multiple KPIs:
```python
score = (
    tardiness_weight * total_tardiness +
    setup_weight * total_setup_time +
    utilization_weight * utilization_imbalance +
    violation_penalty * num_violations
)
```

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
python test_complete_system.py
```

This tests both simplified and comprehensive agent systems.

### Manual API Testing

Use the interactive API docs at http://localhost:8000/docs to test endpoints manually.

---

## 📊 Performance Metrics

The system tracks and optimizes for:

| Metric | Description | Goal |
|--------|-------------|------|
| **Total Tardiness** | Sum of delays past due dates | Minimize |
| **Setup Time** | Total time spent on changeovers | Minimize |
| **Machine Utilization** | Balance of work across machines | Maximize & Balance |
| **Rush Order On-Time %** | Rush orders completed on time | Maximize |
| **Constraint Violations** | Number of rule violations | Zero |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Documentation

Additional documentation available:

- **[agents-architecture.md](agents-architecture.md)** - Detailed agent architecture and rules
- **[backend/AGENTS_README.md](backend/AGENTS_README.md)** - Complete implementation guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation notes
- **[MODE_COMPARISON.md](MODE_COMPARISON.md)** - Comparison of agent modes

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.10+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Ensure `.env` file exists with `GROQ_API_KEY`

### Frontend won't start
- Check Node version: `node --version` (needs 18+)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check port 5173 is not in use

### API errors
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Validate request format against `/docs`

### LLM errors
- Verify `GROQ_API_KEY` is set correctly in `.env`
- Check API key is valid at https://console.groq.com
- Monitor rate limits and quotas

---


## 🙏 Acknowledgments

- **LangChain** - For the excellent LLM framework
- **LangGraph** - For multi-agent orchestration
- **Groq** - For high-performance LLM inference
- **FastAPI** - For the modern API framework
- **React** - For the UI library

---



