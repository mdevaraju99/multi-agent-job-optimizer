"""
Baseline FIFO Scheduler - Simple First-In-First-Out scheduling
"""

from typing import List, Tuple
from datetime import time
from collections import defaultdict

from models.job import Job
from models.machine import Machine, Constraint
from models.schedule import Schedule, JobAssignment


class BaselineScheduler:
    """
    Simple FIFO (First-In-First-Out) scheduler for baseline comparison.
    
    This scheduler assigns jobs in order of priority (rush first) then
    due time, without sophisticated optimization.
    """
    
    def schedule(
        self,
        jobs: List[Job],
        machines: List[Machine],
        constraint: Constraint
    ) -> Tuple[Schedule, str]:
        """
        Create a baseline FIFO schedule.
        
        Args:
            jobs: List of jobs to schedule
            machines: Available machines
            constraint: Scheduling constraints
            
        Returns:
            Tuple of (Schedule, explanation)
        """
        # Sort jobs: rush first, then by due time
        sorted_jobs = sorted(
            jobs,
            key=lambda j: (0 if j.is_rush else 1, j.due_time)
        )
        
        schedule = Schedule()
        current_time = {m.machine_id: constraint.shift_start for m in machines}
        current_product = {m.machine_id: None for m in machines}
        
        for job in sorted_jobs:
            # Find first compatible machine
            compatible = [
                m for m in machines
                if m.can_produce(job.product_type) and job.can_run_on(m.machine_id)
            ]
            
            if not compatible:
                continue
            
            # Use first available machine
            best_machine = compatible[0]
            machine_id = best_machine.machine_id
            
            # Calculate setup time
            prev_product = current_product[machine_id]
            if prev_product:
                setup_time = constraint.get_setup_time(prev_product, job.product_type)
            else:
                setup_time = 0
            
            # Calculate time slot
            start_min = current_time[machine_id].hour * 60 + current_time[machine_id].minute + setup_time
            end_min = start_min + job.processing_time
            
            # Check shift boundary
            shift_end_min = constraint.shift_end.hour * 60 + constraint.shift_end.minute + constraint.max_overtime_minutes
            if end_min > shift_end_min:
                continue  # Skip if won't fit
            
            start_time = time(start_min // 60, start_min % 60)
            end_time = time(min(end_min // 60, 23), end_min % 60)
            
            # Create assignment
            assignment = JobAssignment(
                job=job,
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
                setup_time_before=setup_time
            )
            
            schedule.add_assignment(assignment)
            
            # Update state
            current_time[machine_id] = end_time
            current_product[machine_id] = job.product_type
        
        explanation = f"""BASELINE FIFO SCHEDULER

Simple first-come-first-served scheduling with no optimization.

STRATEGY:
- Rush jobs prioritized first
- Then sorted by due time
- Assigned to first compatible machine
- No load balancing or setup optimization

RESULT:
- Scheduled: {len(schedule.get_all_jobs())} / {len(jobs)} jobs
- This serves as a baseline for comparison with optimized schedules
"""
        
        schedule.explanation = explanation
        return schedule, explanation
