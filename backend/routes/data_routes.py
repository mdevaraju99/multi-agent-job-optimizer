from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from models.schemas import Job, MachineDowntime
from models.data_generator import generate_random_jobs, generate_random_downtime
from utils.csv_handler import parse_jobs_csv, parse_downtime_csv

router = APIRouter(prefix="/data", tags=["Data"])

@router.post("/generate-random", response_model=dict)
async def generate_random_data(job_count: int = 20, rush_prob: float = 0.2, downtime_count: int = 0, machine_count: int = 4):
    jobs = generate_random_jobs(job_count, rush_prob, machine_count)
    downtimes = generate_random_downtime(downtime_count, machine_count)
    return {
        "jobs": jobs,
        "downtimes": downtimes
    }

@router.post("/generate-downtime", response_model=List[MachineDowntime])
async def generate_downtime_only(count: int = 1, machine_count: int = 4):
    return generate_random_downtime(count, machine_count)

@router.post("/upload-jobs", response_model=List[Job])
async def upload_jobs(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    try:
        jobs = parse_jobs_csv(content)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-downtime", response_model=List[MachineDowntime])
async def upload_downtime(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    try:
        downtimes = parse_downtime_csv(content)
        return downtimes
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
