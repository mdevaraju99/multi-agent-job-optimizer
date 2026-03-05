"""
Configuration Loader - Load machines and constraints from config
"""

from datetime import time
from typing import Dict, Any

from models.machine import Machine, Constraint, DowntimeWindow


def load_config() -> Dict[str, Any]:
    """
    Load default configuration for machines and constraints.
    
    Returns:
        Dictionary with 'machines' and 'constraint' keys
    """
    # Define machines
    machines = [
        Machine(
            "M1",
            ["P_A", "P_B"],
            downtime_windows=[
                DowntimeWindow(time(10, 0), time(10, 30), "Scheduled Maintenance")
            ]
        ),
        Machine(
            "M2",
            ["P_A", "P_B", "P_C"],
            downtime_windows=[]
        ),
        Machine(
            "M3",
            ["P_B", "P_C"],
            downtime_windows=[
                DowntimeWindow(time(14, 0), time(14, 30), "Quality Inspection")
            ]
        )
    ]
    
    # Define constraints
    constraint = Constraint(
        shift_start=time(8, 0),
        shift_end=time(16, 0),
        max_overtime_minutes=60,
        setup_times={
            "P_A->P_A": 5,
            "P_A->P_B": 30,
            "P_A->P_C": 25,
            "P_B->P_A": 30,
            "P_B->P_B": 5,
            "P_B->P_C": 25,
            "P_C->P_A": 25,
            "P_C->P_B": 25,
            "P_C->P_C": 5,
        },
        priority_weights={
            "tardiness": 2.0,
            "setup_time": 1.0,
            "utilization": 1.5,
            "rush_penalty": 5.0
        }
    )
    
    return {
        "machines": machines,
        "constraint": constraint
    }
