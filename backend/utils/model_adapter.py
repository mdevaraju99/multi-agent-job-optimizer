"""
Model Adapter - Bridge between Pydantic schemas and class-based models

This adapter converts between the existing Pydantic schemas (used by current agents)
and the new class-based models (used by comprehensive LangGraph agents).
"""

from datetime import time as dt_time, datetime
from typing import List, Dict

# Import existing Pydantic schemas
from models.schemas import (
    Job as SchemaJob,
    MachineDowntime as SchemaDowntime,
    ShiftConstraints as SchemaConstraints,
    ScheduledJob as SchemaScheduledJob,
    AgentResult as SchemaAgentResult
)

# Import new class-based models
from models.job import Job
from models.machine import Machine, Constraint, DowntimeWindow
from models.schedule import Schedule, JobAssignment, KPI


def parse_time(time_str: str) -> dt_time:
    """Parse HH:MM string to time object."""
    parts = time_str.split(':')
    return dt_time(int(parts[0]), int(parts[1]))


def time_to_str(t: dt_time) -> str:
    """Convert time object to HH:MM string."""
    return t.strftime("%H:%M")


class ModelAdapter:
    """Adapter to convert between schema and class-based models."""
    
    @staticmethod
    def schema_job_to_job(schema_job: SchemaJob) -> Job:
        """Convert Pydantic Job to class-based Job."""
        due_time = parse_time(schema_job.due_time) if schema_job.due_time else dt_time(16, 0)
        priority = "rush" if schema_job.priority.value == "Rush" else "normal"
        
        return Job(
            job_id=schema_job.job_id,
            product_type=schema_job.product_type,
            processing_time=schema_job.processing_time,
            due_time=due_time,
            priority=priority,
            machine_compatibility=schema_job.machine_options
        )
    
    @staticmethod
    def jobs_to_schema(jobs: List[Job]) -> List[SchemaJob]:
        """Convert list of class-based Jobs to Pydantic Jobs."""
        schema_jobs = []
        for job in jobs:
            schema_jobs.append(SchemaJob(
                job_id=job.job_id,
                product_type=job.product_type,
                machine_options=job.machine_compatibility or [],
                processing_time=job.processing_time,
                due_time=time_to_str(job.due_time) if job.due_time else None,
                priority="Rush" if job.is_rush else "Normal"
            ))
        return schema_jobs
    
    @staticmethod
    def downtimes_to_machines(
        downtimes: List[SchemaDowntime],
        machine_ids: List[str] = None
    ) -> List[Machine]:
        """
        Convert downtime list to Machine objects.
        
        Args:
            downtimes: List of downtime periods
            machine_ids: Optional list of machine IDs to create
            
        Returns:
            List of Machine objects with capabilities and downtimes
        """
        if machine_ids is None:
            # Extract unique machine IDs from downtimes
            machine_ids = list(set(dt.machine_id for dt in downtimes))
            if not machine_ids:
                machine_ids = ["M1", "M2", "M3"]  # Default machines
        
        machines = []
        for machine_id in machine_ids:
            # Define capabilities (can be customized)
            if machine_id == "M1":
                capabilities = ["P_A", "P_B"]
            elif machine_id == "M2":
                capabilities = ["P_A", "P_B", "P_C"]
            elif machine_id == "M3":
                capabilities = ["P_B", "P_C"]
            else:
                capabilities = ["P_A", "P_B", "P_C"]  # Default: can produce all
            
            # Get downtimes for this machine
            machine_downtimes = [
                DowntimeWindow(
                    start_time=parse_time(dt.start_time),
                    end_time=parse_time(dt.end_time),
                    reason=dt.reason
                )
                for dt in downtimes
                if dt.machine_id == machine_id
            ]
            
            machines.append(Machine(
                machine_id=machine_id,
                capabilities=capabilities,
                downtime_windows=machine_downtimes
            ))
        
        return machines
    
    @staticmethod
    def schema_constraints_to_constraint(schema_constraints: SchemaConstraints) -> Constraint:
        """Convert Pydantic ShiftConstraints to class-based Constraint."""
        return Constraint(
            shift_start=parse_time(schema_constraints.start_time),
            shift_end=parse_time(schema_constraints.end_time),
            max_overtime_minutes=60,  # Default
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
    
    @staticmethod
    def schedule_to_schema_result(
        schedule: Schedule,
        agent_name: str,
        jobs: List[Job],
        machines: List[Machine],
        constraint: Constraint
    ) -> SchemaAgentResult:
        """
        Convert class-based Schedule to Pydantic AgentResult.
        
        Args:
            schedule: Schedule to convert
            agent_name: Name of the agent
            jobs: Original job list
            machines: Machine list
            constraint: Constraints
            
        Returns:
            Pydantic AgentResult
        """
        # Calculate KPIs if not already done
        if schedule.kpis is None:
            schedule.calculate_kpis(machines, constraint)
        
        # Convert assignments to schema scheduled jobs
        schema_schedules: Dict[str, List[SchemaScheduledJob]] = {}
        
        for machine_id, assignments in schedule.assignments.items():
            schema_jobs = []
            for assignment in assignments:
                schema_jobs.append(SchemaScheduledJob(
                    job_id=assignment.job.job_id,
                    machine_id=assignment.machine_id,
                    start_time=time_to_str(assignment.start_time),
                    end_time=time_to_str(assignment.end_time),
                    product_type=assignment.job.product_type,
                    is_setup=False,
                    notes=f"Setup: {assignment.setup_time_before}min" if assignment.setup_time_before > 0 else None
                ))
            schema_schedules[machine_id] = schema_jobs
        
        # Create KPI result
        from models.schemas import KPIResult
        kpi_result = KPIResult(
            total_jobs=schedule.kpis.num_jobs_total,
            completed_jobs=schedule.kpis.num_jobs_scheduled,
            total_tardiness=schedule.kpis.total_tardiness,
            total_setup_time=schedule.kpis.total_setup_time,
            makespan=constraint.get_shift_duration_minutes(),
            bottleneck_machine="N/A",
            score=schedule.kpis.get_weighted_score(constraint)
        )
        
        return SchemaAgentResult(
            agent_name=agent_name,
            schedules=schema_schedules,
            kpis=kpi_result,
            explanation=schedule.explanation,
            violations=[]
        )


# Example usage
if __name__ == "__main__":
    # Test conversion
    schema_job = SchemaJob(
        job_id="J001",
        product_type="P_A",
        machine_options=["M1", "M2"],
        processing_time=45,
        due_time="12:00",
        priority="Rush"
    )
    
    job = ModelAdapter.schema_job_to_job(schema_job)
    print(f"Converted: {job}")
    print(f"Is rush: {job.is_rush}")
