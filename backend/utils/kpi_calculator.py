from typing import List, Dict
from datetime import datetime, timedelta
from models.schemas import ScheduledJob, Job, MachineSchedule, KPIResult

def parse_time(t_str: str) -> datetime:
    # Assumes HH:MM format and current day
    now = datetime.now()
    t = datetime.strptime(t_str, "%H:%M").time()
    return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

def calculate_kpis(schedules: Dict[str, List[ScheduledJob]], all_jobs: List[Job]) -> KPIResult:
    """
    Calculate KPIs:
    1. Tardiness: Total minutes jobs are late
    2. Setup Time: 10 min for each product switch on each machine
    3. Product Switches: Number of product changes
    4. Load Balance: Variance in machine utilization
    """
    total_jobs = len(all_jobs)
    scheduled_jobs_count = sum(len(jobs) for jobs in schedules.values())
    
    total_tardiness = 0
    total_setup_time = 0
    total_switches = 0
    machine_end_times = []
    machine_loads = {}
    
    job_map = {j.job_id: j for j in all_jobs}
    
    for machine_id, jobs in schedules.items():
        if not jobs:
            continue
            
        # Sort by start time
        sorted_jobs = sorted(jobs, key=lambda x: parse_time(x.start_time))
        
        last_product = None
        machine_start = None
        machine_end = None
        
        for s_job in sorted_jobs:
            # Count product switches - every time product type changes
            if last_product is not None and last_product != s_job.product_type:
                total_switches += 1
                total_setup_time += 10  # 10 min setup penalty per switch
            
            last_product = s_job.product_type
            
            # Track machine utilization
            if machine_start is None:
                machine_start = parse_time(s_job.start_time)
            machine_end = parse_time(s_job.end_time)
            
            # Calculate tardiness
            original_job = job_map.get(s_job.job_id)
            if original_job and original_job.due_time:
                due = parse_time(original_job.due_time)
                end = parse_time(s_job.end_time)
                if end > due:
                    tardiness = (end - due).total_seconds() / 60
                    total_tardiness += tardiness
        
        if machine_end:
            machine_end_times.append(machine_end)
            # Calculate actual working time for this machine
            shift_start = parse_time("08:00")
            working_time = (machine_end - shift_start).total_seconds() / 60
            machine_loads[machine_id] = working_time

    # Makespan: Time from shift start to last job completion
    makespan = 0
    if machine_end_times:
        shift_start = parse_time("08:00")
        latest_end = max(machine_end_times)
        makespan = (latest_end - shift_start).total_seconds() / 60

    # Bottleneck: Machine with highest load
    bottleneck_machine = "None"
    if machine_loads:
        bottleneck_machine = max(machine_loads.items(), key=lambda x: x[1])[0]

    # Load Balance Variance: Lower is better (more balanced)
    load_balance_variance = 0.0
    if machine_loads:
        loads = list(machine_loads.values())
        if len(loads) > 1:
            mean_load = sum(loads) / len(loads)
            variance = sum((x - mean_load) ** 2 for x in loads) / len(loads)
            load_balance_variance = variance

    # Score calculation:
    # Higher is better. Penalize tardiness heavily, setup moderately
    # Perfect score (100) = no tardiness, no setup, all jobs scheduled, balanced load
    completion_bonus = (scheduled_jobs_count / total_jobs) * 40 if total_jobs > 0 else 0
    tardiness_penalty = min(total_tardiness * 0.3, 30)  # Max 30 point penalty
    setup_penalty = min(total_setup_time * 0.2, 20)  # Max 20 point penalty
    balance_penalty = min(load_balance_variance * 0.01, 10)  # Max 10 point penalty
    
    score = max(0.0, completion_bonus + 60 - tardiness_penalty - setup_penalty - balance_penalty)

    return KPIResult(
        total_jobs=total_jobs,
        completed_jobs=scheduled_jobs_count,
        total_tardiness=int(total_tardiness),
        total_setup_time=int(total_setup_time),
        product_switches=total_switches,
        load_balance_variance=round(load_balance_variance, 2),
        makespan=int(makespan),
        bottleneck_machine=bottleneck_machine,
        score=round(score, 2)
    )
