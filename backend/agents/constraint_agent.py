from typing import List, Dict
from datetime import datetime
from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult, ScheduledJob
from utils.kpi_calculator import parse_time
from .base_agent import BaseAgent

class ConstraintAgent(BaseAgent):
    """
    CONSTRAINT AGENT (from architecture):
    - Validates schedules against ALL operational constraints
    - Checks shift boundaries, downtime conflicts, machine compatibility
    - Enforces Rush job priority rules
    - Returns detailed violation reports
    - MUST BE ZERO violations for valid schedule
    """
    def __init__(self):
        super().__init__("Constraint Agent")

    async def optimize(self, jobs, downtimes, constraints):
        # Constraint agent doesn't optimize, it validates
        return AgentResult(
            agent_name=self.name,
            schedules={},
            kpis=None, # type: ignore
            explanation="Constraint Agent performs validation only.",
            violations=[]
        )

    def validate(
        self, 
        schedules: Dict[str, List[ScheduledJob]], 
        jobs: List[Job],
        downtimes: List[MachineDowntime],
        constraints: ShiftConstraints
    ) -> List[str]:
        """
        COMPREHENSIVE VALIDATION (from architecture):
        1. Job Assignment Check - all jobs assigned
        2. Shift Boundary Check - within shift + overtime
        3. Machine Compatibility Check
        4. Downtime Conflict Check
        5. Time Overlap Check (same machine)
        6. Rush Job Deadline Check (CRITICAL)
        """
        violations = []
        shift_end = parse_time(constraints.end_time)
        shift_start = parse_time(constraints.start_time)
        
        job_map = {j.job_id: j for j in jobs}
        
        # 1. CHECK: All jobs assigned
        scheduled_job_ids = set()
        for job_list in schedules.values():
            for s_job in job_list:
                scheduled_job_ids.add(s_job.job_id)
        
        unassigned_jobs = [j.job_id for j in jobs if j.job_id not in scheduled_job_ids]
        if unassigned_jobs:
            violations.append(f"Not all jobs assigned. Missing: {', '.join(unassigned_jobs)}")
        
        # 2-6: Per-job checks
        for m_id, job_list in schedules.items():
            # Sort by start time for overlap detection
            sorted_jobs = sorted(job_list, key=lambda x: parse_time(x.start_time))
            
            for idx, s_job in enumerate(sorted_jobs):
                j_start = parse_time(s_job.start_time)
                j_end = parse_time(s_job.end_time)
                
                original_job = job_map.get(s_job.job_id)
                
                # 2. CHECK: Shift boundary (no overtime in this version)
                if j_end > shift_end:
                    overtime_min = int((j_end - shift_end).total_seconds() / 60)
                    violations.append(f"Job {s_job.job_id} on {m_id} ends at {s_job.end_time}, exceeds shift end by {overtime_min} min.")
                
                # 3. CHECK: Machine compatibility
                if original_job and m_id not in original_job.machine_options:
                    violations.append(f"Job {s_job.job_id} assigned to incompatible machine {m_id}.")

                # 4. CHECK: Downtime conflicts
                machine_downtimes = [dt for dt in downtimes if dt.machine_id == m_id]
                for dt in machine_downtimes:
                    dt_start = parse_time(dt.start_time)
                    dt_end = parse_time(dt.end_time)
                    
                    if j_start < dt_end and j_end > dt_start:
                        violations.append(f"Job {s_job.job_id} on {m_id} overlaps with downtime {dt.start_time}-{dt.end_time}.")
                
                # 5. CHECK: Time overlaps on same machine
                if idx < len(sorted_jobs) - 1:
                    next_job = sorted_jobs[idx + 1]
                    next_start = parse_time(next_job.start_time)
                    if j_end > next_start:
                        overlap_min = int((j_end - next_start).total_seconds() / 60)
                        violations.append(f"Job {s_job.job_id} overlaps with {next_job.job_id} on {m_id} by {overlap_min} min.")
                
                # 6. CHECK: Rush job deadlines (CRITICAL)
                if original_job and original_job.priority == "Rush" and original_job.due_time:
                    due = parse_time(original_job.due_time)
                    if j_end > due:
                        tardiness_min = int((j_end - due).total_seconds() / 60)
                        violations.append(f"CRITICAL: Rush job {s_job.job_id} is {tardiness_min} min late (due {original_job.due_time}, ends {s_job.end_time})")
                        
        return violations
