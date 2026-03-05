import os
from datetime import datetime, timedelta
from collections import defaultdict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult, ScheduledJob
from utils.kpi_calculator import calculate_kpis, parse_time
from .constraint_agent import ConstraintAgent

class BottleneckAgent:
    def __init__(self):
        self.name = "BottleneckAgent"
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    async def optimize(self, jobs, downtimes, constraints):
        """
        BOTTLENECK AGENT (from architecture):
        - Detects machines with excessive load
        - Identifies underutilized machines
        - Re-routes compatible jobs to balance workload
        - Prioritizes Rush jobs always
        """
        print("[Bottleneck Agent] Optimizing for bottleneck relief...")
        
        # Get all unique machine IDs from jobs
        all_machine_ids = set()
        for job in jobs:
            all_machine_ids.update(job.machine_options)
        
        machine_loads = {mid: 0 for mid in all_machine_ids}
        schedules = defaultdict(list)
        unassigned_count = 0
        violations = []

        shift_start = parse_time(constraints.start_time)
        shift_end = parse_time(constraints.end_time)

        sorted_jobs = sorted(jobs, key=lambda j: (
            0 if j.priority.lower() == 'rush' else 1,
            j.due_time or "23:59"
        ))

        machine_last_product = {mid: None for mid in all_machine_ids}
        machine_end_times = {mid: shift_start for mid in all_machine_ids}  # Track actual end time, not just load

        for job in sorted_jobs:
            candidates = [mid for mid in all_machine_ids if mid in job.machine_options]
            if not candidates:
                unassigned_count += 1
                violations.append(f"Job {job.job_id} has no compatible machines.")
                continue

            # Sort by current load (least-loaded first)
            candidates.sort(key=lambda mid: machine_loads[mid])

            assigned = False
            for mid in candidates:
                last_product = machine_last_product[mid]

                # Setup penalty - 10 min if product types differ
                setup_time = 0
                if last_product and last_product != job.product_type:
                    setup_time = 10

                # Current end time for this machine (ACTUAL end time, not accumulated load)
                current_end = machine_end_times[mid]
                
                # Job starts AFTER setup time (setup is a gap, not part of job)
                job_start = current_end + timedelta(minutes=setup_time)
                job_duration = timedelta(minutes=job.processing_time)

                # Check downtime - job must fit after setup
                job_start = self.skip_downtime(mid, job_start, job_duration, downtimes)

                job_end = job_start + job_duration

                # Check shift boundary
                if job_end > shift_end:
                    continue

                # Assign job
                scheduled_job = ScheduledJob(
                    job_id=job.job_id,
                    machine_id=mid,
                    start_time=job_start.strftime("%H:%M"),
                    end_time=job_end.strftime("%H:%M"),
                    product_type=job.product_type,
                    is_setup=False,
                    notes=f"Setup: {setup_time}min" if setup_time > 0 else None
                )
                schedules[mid].append(scheduled_job)

                # Update machine end time to ACTUAL end of this job
                machine_end_times[mid] = job_end
                
                # Update load tracking for bottleneck calculation
                total_time_used = setup_time + job.processing_time
                machine_loads[mid] = machine_loads[mid] + total_time_used
                
                machine_last_product[mid] = job.product_type
                assigned = True
                break

            if not assigned:
                unassigned_count += 1
                violations.append(f"Job {job.job_id} could not be assigned in Bottleneck optim.")

        # Calculate KPIs
        kpis = calculate_kpis(schedules, jobs)
        
        # Validate constraints
        constraint_agent = ConstraintAgent()
        constraint_violations = constraint_agent.validate(schedules, jobs, downtimes, constraints)
        violations.extend(constraint_violations)
        
        explanation = await self._generate_explanation(kpis, machine_loads)

        return AgentResult(
            agent_name=self.name,
            schedules=schedules,
            kpis=kpis,
            explanation=explanation,
            violations=violations
        )

    def skip_downtime(self, mid, start, dur_td, downtimes):
        """Push start time past any downtimes on this machine."""
        def parse_time(t_str):
            return datetime.strptime(t_str, "%H:%M").replace(
                year=start.year, month=start.month, day=start.day
            )

        dts = sorted([d for d in downtimes if d.machine_id == mid], key=lambda x: x.start_time)
        for dt in dts:
            dt_s = parse_time(dt.start_time)
            dt_e = parse_time(dt.end_time)
            if dt_s <= start < dt_e: start = dt_e
            elif start < dt_s < (start + dur_td): start = dt_e
        return start

    async def _generate_explanation(self, kpis, loads):
        try:
            load_str = ", ".join([f"{k}: {v} min" for k,v in loads.items()])
            prompt = ChatPromptTemplate.from_template(
                """
You are a Bottleneck Analysis & Load Balancing Agent for pharmaceutical production. Provide a DETAILED explanation:

BOTTLENECK AGENT ANALYSIS:

Load Distribution:
- Current machine loads: {load_str}
- Bottleneck machine: {bottleneck}
- Load balance quality: Evaluate variance across production lines

Bottleneck Mitigation:
- How pharmaceutical jobs were distributed to avoid overloading specific production lines
- Identify underutilized machines  

Resource Optimization:
- Machines at capacity vs available time
- Overall utilization rate for pharmaceutical production

IMPLEMENTATION:
- Makespan: {makespan} minutes
- Load balancing strategy applied

RESULT:
- Load balanced across pharmaceutical production lines
- Bottlenecks minimized
                """
            )
            chain = prompt | self.llm
            res = await chain.ainvoke({
                "makespan": kpis.makespan,
                "load_str": load_str,
                "bottleneck": kpis.bottleneck_machine
            })
            return res.content
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
