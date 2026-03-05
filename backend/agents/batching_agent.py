from typing import List, Dict, Any
from datetime import timedelta
from collections import defaultdict
import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult, ScheduledJob
from utils.kpi_calculator import calculate_kpis, parse_time
from .base_agent import BaseAgent
from .constraint_agent import ConstraintAgent
from config import settings

class BatchingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Batching Agent")
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.FAST_MODEL_NAME
        )

    async def optimize(
        self, 
        jobs: List[Job], 
        downtimes: List[MachineDowntime], 
        constraints: ShiftConstraints
    ) -> AgentResult:
        self.log("Optimizing for minimal setup times...")
        
        # BATCHING ALGORITHM (from architecture):
        # Step 1: Group jobs by product_type
        # Step 2: Within each product group, prioritize Rush jobs
        # Step 3: Sort by due_time within priority level
        
        ordered_jobs = sorted(jobs, key=lambda x: (
            x.product_type,  # Group by product first
            0 if x.priority == "Rush" else 1,  # Rush jobs first within product
            x.due_time or "23:59"  # Then by deadline
        ))
        
        # Try to assign to machine that last processed this product type
        # to minimize setup switches
        
        schedules: Dict[str, List[ScheduledJob]] = {}
        machine_states = {} # machine_id -> {end_time: dt, last_product: str}
        shift_start = parse_time(constraints.start_time)

        violations = []
        unassigned_count = 0

        for job in ordered_jobs:
            best_machine = None
            earliest_start = None
            selected_setup_time = 0
            
            for m_id in job.machine_options:
                state = machine_states.get(m_id, {"end_time": shift_start, "last_product": None})
                current_time = state["end_time"]
                last_product = state["last_product"]
                
                # Setup time logic
                setup_duration = self.calculate_setup_time(last_product, job.product_type)
                
                # Check downtimes (simplified from BaselineAgent)
                # ... (Logic to skip downtime) ...
                # Use a helper to find valid start including setup
                
                actual_start = self._find_start_time(current_time, setup_duration, job.processing_time, m_id, downtimes)
                
                if best_machine is None or actual_start < earliest_start:
                    best_machine = m_id
                    earliest_start = actual_start
                    selected_setup_time = setup_duration
            
            if best_machine:
                end_time = earliest_start + timedelta(minutes=job.processing_time)
                
                # Record setup job if needed
                if selected_setup_time > 0:
                    # In this model, setup is part of the gap, but we can visualize it?
                    # Let's mark the job as having setup or insert a setup block. 
                    # For simplicity, we just mark the job 'is_setup=True' (conceptually wrong, setup is separate).
                    # Better: The 'start_time' includes the setup? No, start_time is when processing starts.
                    # The gap before is setup.
                    pass

                scheduled_job = ScheduledJob(
                    job_id=job.job_id,
                    machine_id=best_machine,
                    start_time=earliest_start.strftime("%H:%M"),
                    end_time=end_time.strftime("%H:%M"),
                    product_type=job.product_type,
                    is_setup=False,  # Never mark jobs as setup
                    notes=f"Setup: {selected_setup_time}min" if selected_setup_time > 0 else None
                )
                
                if best_machine not in schedules:
                    schedules[best_machine] = []
                schedules[best_machine].append(scheduled_job)
                
                machine_states[best_machine] = {
                    "end_time": end_time,
                    "last_product": job.product_type
                }
            else:
                unassigned_count += 1
                violations.append(f"Job {job.job_id} could not be assigned in Batching optim.")

        kpis = calculate_kpis(schedules, jobs)
        
        # Validate constraints
        constraint_agent = ConstraintAgent()
        constraint_violations = constraint_agent.validate(schedules, jobs, downtimes, constraints)
        violations.extend(constraint_violations)
        
        # Generate Explanation via Groq
        explanation = await self._generate_explanation(kpis)
        
        return AgentResult(
            agent_name=self.name,
            schedules=schedules,
            kpis=kpis,
            explanation=explanation,
            violations=violations
        )

    def _find_start_time(self, current_time, setup_minutes, processing_minutes, machine_id, downtimes):
        # Add setup first
        start_check = current_time + timedelta(minutes=setup_minutes)
        job_duration = timedelta(minutes=processing_minutes)
        
        # Sort downtimes
        machine_downtimes = sorted([d for d in downtimes if d.machine_id == machine_id], key=lambda x: x.start_time)
        
        for dt in machine_downtimes:
            dt_start = parse_time(dt.start_time)
            dt_end = parse_time(dt.end_time)
            
            # If our start (with setup) overlaps downtime
            if dt_start <= start_check < dt_end:
                 start_check = dt_end
            # If job execution overlaps
            elif start_check < dt_start < (start_check + job_duration):
                 start_check = dt_end
                 
        return start_check

    async def _generate_explanation(self, kpis):
        try:
            prompt = ChatPromptTemplate.from_template(
                """
You are a Batching & Setup Minimization Agent for a pharmaceutical production facility. Provide a DETAILED explanation following this exact format:

BATCHING AGENT RECOMMENDATIONS:

Batching Strategy:
- Identify Rush Jobs: List all rush jobs with their product types and deadlines
- Batching Groups: Group jobs by pharmaceutical product (Paracetamol, Ibuprofen, Amoxicillin, Aspirin, Metformin)
- Sequence Priority: Explain the order (rush first, then by product type, then deadline)

Setup Optimization:
- Explain how pharmaceutical jobs were grouped to minimize equipment setup/cleaning changes
- Specify setup time savings achieved (changeover between different medications)
- Mention product type transitions and equipment preparation

Recommended Sequence:
- List the actual job sequence with pharmaceutical product types
- Mark rush jobs clearly
- Show the logical flow

IMPLEMENTATION:
- Number of pharmaceutical product types grouped
- Number of rush jobs prioritized  
- Total jobs scheduled: {completed} / {total}
- Total setup time: {setup_time} minutes
- Optimization score: {score}

RESULT:
- Jobs successfully scheduled
- Setup time minimization achieved
- Rush jobs handled appropriately
                """
            )
            chain = prompt | self.llm
            res = await chain.ainvoke({
                "setup_time": kpis.total_setup_time,
                "completed": kpis.completed_jobs,
                "total": kpis.total_jobs,
                "score": kpis.score
            })
            return res.content
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
