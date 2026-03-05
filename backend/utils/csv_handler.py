import pandas as pd
from typing import List, Union
from io import BytesIO
from models.schemas import Job, MachineDowntime, JobPriority

def parse_jobs_csv(file_content: bytes) -> List[Job]:
    try:
        df = pd.read_csv(BytesIO(file_content))
        required_cols = ["job_id", "product_type", "machine_options", "processing_time", "priority", "due_time"]
        
        # Check columns
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
        jobs = []
        for _, row in df.iterrows():
            # Handle list parsing for machine_options
            machines = row["machine_options"]
            if isinstance(machines, str):
                machines = [m.strip() for m in machines.split(';')] # Semicolon separated in CSV preferably
            
            # Priority is now required
            priority = JobPriority.NORMAL
            if str(row["priority"]).lower() == "rush":
                priority = JobPriority.RUSH
                
            # Due time is now required
            if pd.isna(row["due_time"]):
                raise ValueError(f"Job {row['job_id']} missing required due_time")
            due_time = str(row["due_time"])

            job = Job(
                job_id=str(row["job_id"]),
                product_type=str(row["product_type"]),
                machine_options=machines,
                processing_time=int(row["processing_time"]),
                due_time=due_time,
                priority=priority
            )
            jobs.append(job)
        return jobs
    except Exception as e:
        raise ValueError(f"Error parsing Jobs CSV: {str(e)}")

def parse_downtime_csv(file_content: bytes) -> List[MachineDowntime]:
    try:
        df = pd.read_csv(BytesIO(file_content))
        required_cols = ["machine_id", "start_time", "end_time"]
        
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
            
        downtimes = []
        for _, row in df.iterrows():
            reason = "Maintenance"
            if "reason" in df.columns and pd.notna(row["reason"]):
                reason = str(row["reason"])
                
            dt = MachineDowntime(
                machine_id=str(row["machine_id"]),
                start_time=str(row["start_time"]),
                end_time=str(row["end_time"]),
                reason=reason
            )
            downtimes.append(dt)
        return downtimes
    except Exception as e:
        raise ValueError(f"Error parsing Downtime CSV: {str(e)}")
