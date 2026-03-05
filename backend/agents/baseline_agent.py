from typing import List, Dict
from datetime import datetime, timedelta
from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult, ScheduledJob
from utils.kpi_calculator import calculate_kpis, parse_time
from .base_agent import BaseAgent
from .constraint_agent import ConstraintAgent

class BaselineAgent(BaseAgent):
    def __init__(self):
        super().__init__("Baseline Agent")

    async def optimize(
        self, 
        jobs: List[Job], 
        downtimes: List[MachineDowntime], 
        constraints: ShiftConstraints
    ) -> AgentResult:
        self.log("Starting FCFS optimization...")
        
        # BASELINE ALGORITHM (from architecture):
        # Sort: Rush jobs first, then by job_id (arrival order)
        # Simple FIFO with NO optimization
        sorted_jobs = sorted(jobs, key=lambda x: (
            0 if x.priority == "Rush" else 1,  # Rush first
            x.job_id  # Then by arrival order
        ))
        
        machine_timelines = {} # Machine ID -> current end time (datetime)
        
        # Initialize timelines to shift start
        shift_start_dt = parse_time(constraints.start_time)
        
        schedules: Dict[str, List[ScheduledJob]] = {}
        
        violations = []
        unassigned_count = 0
        
        for job in sorted_jobs:
            # ... (existing loop logic)
            # Find best machine: available earliest
            best_machine = None
            earliest_start = None
            
            # Filter valid machines for this job
            valid_machines = job.machine_options
            
            for m_id in valid_machines:
                timelines_for_comparison = machine_timelines.get(m_id, {"time": shift_start_dt, "product": None})
                current_time = timelines_for_comparison["time"]
                last_prod = timelines_for_comparison["product"]
                
                # Setup
                setup_minutes = self.calculate_setup_time(last_prod, job.product_type)
                
                # Check for downtime overlap (Simplified: if current_time is in downtime, jump to end)
                # In a real scheduler, we'd look ahead. Here: just check if we start now, do we overlap?
                # Actually, simply find the earliest time this job can start on this machine
                
                # Apply downtime check loop
                start_candidate = current_time + timedelta(minutes=setup_minutes)
                job_duration = timedelta(minutes=job.processing_time)
                
                # Check against all downtimes for this machine
                machine_downtimes = [d for d in downtimes if d.machine_id == m_id]
                machine_downtimes.sort(key=lambda x: parse_time(x.start_time))
                
                for dt in machine_downtimes:
                    dt_start = parse_time(dt.start_time)
                    dt_end = parse_time(dt.end_time)
                    
                    # If candidate start is during downtime, push it
                    if dt_start <= start_candidate < dt_end:
                        start_candidate = dt_end
                    # If job interval overlaps downtime
                    elif start_candidate < dt_start < (start_candidate + job_duration):
                        start_candidate = dt_end
                
                if best_machine is None or start_candidate < earliest_start:
                    best_machine = m_id
                    earliest_start = start_candidate
            
            if best_machine:
                # Assign
                end_time = earliest_start + timedelta(minutes=job.processing_time)
                
                scheduled_job = ScheduledJob(
                    job_id=job.job_id,
                    machine_id=best_machine,
                    start_time=earliest_start.strftime("%H:%M"),
                    end_time=end_time.strftime("%H:%M"),
                    product_type=job.product_type
                )
                
                if best_machine not in schedules:
                    schedules[best_machine] = []
                schedules[best_machine].append(scheduled_job)
                
                machine_timelines[best_machine] = {
                    "time": end_time,
                    "product": job.product_type
                }
            else:
                unassigned_count += 1
                violations.append(f"Job {job.job_id} could not be assigned (No valid slot found).")
        
        kpis = calculate_kpis(schedules, jobs)
        
        # Validate constraints
        constraint_agent = ConstraintAgent()
        constraint_violations = constraint_agent.validate(schedules, jobs, downtimes, constraints)
        violations.extend(constraint_violations)
        
        explanation = f"""
BASELINE AGENT (FCFS - Pharmaceutical Production):

Strategy:
- First-Come-First-Served scheduling for medication production
- Rush orders (urgent pharmaceutical orders) prioritized first
- Jobs processed in order received after rush orders
- No advanced optimization applied

Results:
- Scheduled: {kpis.completed_jobs}/{len(jobs)} jobs
- Makespan: {kpis.makespan} minutes
- Total Tardiness: {kpis.total_tardiness} minutes
- Setup Time: {kpis.total_setup_time} minutes

Performance:
- Violations: {len(violations)} issues
- Unassigned jobs: {unassigned_count}
- Simple priority-based FCFS approach
- Equipment setup/cleaning penalty (10 min) applied for pharmaceutical product changes

This baseline provides a reference point for AI optimization strategies in pharmaceutical manufacturing.
"""
        
        return AgentResult(
            agent_name=self.name,
            schedules=schedules,
            kpis=kpis,
            explanation=explanation,
            violations=violations
        )
