"""
Core data models package for the Multi-Agent Production Job Optimizer.

This package contains all data structures used throughout the system:
- Job: Represents a production job to be scheduled
- Machine: Represents a production machine with constraints
- Schedule: Represents a complete production schedule
- KPI: Key Performance Indicators for schedule evaluation
- Constraint: Scheduling constraints and business rules
"""

from .job import Job
from .machine import Machine, Constraint, DowntimeWindow
from .schedule import Schedule, KPI, JobAssignment

# Import schemas for backward compatibility
try:
    from .schemas import (
        Job as SchemaJob,
        JobPriority,
        MachineDowntime,
        ShiftConstraints,
        SetupConfig,
        OptimizationRequest,
        ScheduledJob,
        MachineSchedule,
        KPIResult,
        AgentResult,
        ComparisonResponse
    )
    
    __all__ = [
        # Core models
        'Job', 'Machine', 'Constraint', 'DowntimeWindow',
        'Schedule', 'KPI', 'JobAssignment',
        # Schemas
        'SchemaJob', 'JobPriority', 'MachineDowntime', 'ShiftConstraints',
        'SetupConfig', 'OptimizationRequest', 'ScheduledJob',
        'MachineSchedule', 'KPIResult', 'AgentResult', 'ComparisonResponse'
    ]
except ImportError:
    __all__ = ['Job', 'Machine', 'Constraint', 'DowntimeWindow', 'Schedule', 'KPI', 'JobAssignment']
