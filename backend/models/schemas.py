from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime, time
from enum import Enum

class JobPriority(str, Enum):
    NORMAL = "Normal"
    RUSH = "Rush"

class Job(BaseModel):
    job_id: str
    product_type: str
    machine_options: List[str]  # List of compatible machine IDs
    processing_time: int  # In minutes
    due_time: Optional[str] = None # HH:MM string
    priority: JobPriority = JobPriority.NORMAL
    
    @validator('machine_options', pre=True)
    def parse_machine_options(cls, v):
        if isinstance(v, str):
            return [m.strip() for m in v.split(',')]
        return v

class MachineDowntime(BaseModel):
    machine_id: str
    start_time: str # HH:MM
    end_time: str # HH:MM
    reason: str = "Unplanned Maintenance"

class ShiftConstraints(BaseModel):
    start_time: str = "08:00"
    end_time: str = "16:00"
    
class SetupConfig(BaseModel):
    same_product_time: int = 15
    different_product_time: int = 60

class OptimizationRequest(BaseModel):
    jobs: List[Job]
    downtimes: List[MachineDowntime] = []
    shift: ShiftConstraints = ShiftConstraints()
    run_simulation: bool = False
    
class ScheduledJob(BaseModel):
    job_id: str
    machine_id: str
    start_time: str
    end_time: str
    product_type: str
    is_setup: bool = False
    notes: Optional[str] = None

class MachineSchedule(BaseModel):
    machine_id: str
    jobs: List[ScheduledJob]
    utilization: float

class KPIResult(BaseModel):
    total_jobs: int
    completed_jobs: int
    total_tardiness: int
    total_setup_time: int
    product_switches: int
    load_balance_variance: float
    makespan: int
    bottleneck_machine: str
    score: float

class AgentResult(BaseModel):
    agent_name: str
    schedules: Dict[str, List[ScheduledJob]] # machine_id -> jobs
    kpis: KPIResult
    explanation: str
    violations: List[str] = []

class ComparisonResponse(BaseModel):
    baseline: AgentResult
    batching: AgentResult
    bottleneck: AgentResult
    orchestrated: AgentResult
    summary: str
