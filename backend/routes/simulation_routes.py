from fastapi import APIRouter
from models.schemas import MachineDowntime, OptimizationRequest, ScheduledJob
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post("/machine-failure", response_model=OptimizationRequest)
async def simulate_failure(request: OptimizationRequest, machine_id: str):
    """
    Injects a sudden machine failure starting NOW (or logic specific time) for 2 hours.
    Returns modified request object with new downtime added.
    """
    # Simply add a downtime to the list
    # Assume 'sudden' means starting from current simulation time or a fixed time?
    # For POC, let's say it starts at 11:00 AM (middle of shift)
    start_time = "11:00"
    end_time = "13:00"
    
    new_downtime = MachineDowntime(
        machine_id=machine_id,
        start_time=start_time,
        end_time=end_time,
        reason="Sudden Failure (Simulation)"
    )
    
    request.downtimes.append(new_downtime)
    return request
