import random
from datetime import datetime, timedelta
from typing import List
from .schemas import Job, JobPriority, MachineDowntime

# PHARMA PRODUCT TYPES (Tablets/Medications)
PRODUCT_TYPES = [
    "Paracetamol_500mg",
    "Ibuprofen_400mg",
    "Amoxicillin_250mg",
    "Aspirin_75mg",
    "Metformin_500mg"
]

def generate_machine_capabilities(num_machines: int):
    """
    Generate machine capability matrix dynamically based on number of machines.
    Each machine can produce 2-4 different products.
    """
    capabilities = {}
    for i in range(num_machines):
        machine_id = f"M{i+1}"
        # Each machine can produce 2-4 random products
        num_products = random.randint(2, min(4, len(PRODUCT_TYPES)))
        capabilities[machine_id] = random.sample(PRODUCT_TYPES, num_products)
    
    # Ensure all products can be made by at least one machine
    for product in PRODUCT_TYPES:
        if not any(product in caps for caps in capabilities.values()):
            random_machine = f"M{random.randint(1, num_machines)}"
            if product not in capabilities[random_machine]:
                capabilities[random_machine].append(product)
    
    return capabilities

def generate_random_jobs(count: int = 20, rush_probability: float = 0.2, num_machines: int = 4) -> List[Job]:
    """
    Generate pharma production jobs with dynamic machine count.
    Format: job_id, product, duration, deadline, priority, compatible_machines
    """
    jobs = []
    base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Generate machine capabilities dynamically
    MACHINE_CAPABILITIES = generate_machine_capabilities(num_machines)
    
    for i in range(count):
        # Job ID
        job_id = f"J{i+1:03d}"
        
        # Product type (Pharma tablets)
        product = random.choice(PRODUCT_TYPES)
        
        # Duration (processing time) based on product type
        if product == "P_A":
            duration = random.choice([30, 45, 60])  # Shorter jobs
        elif product == "P_B":
            duration = random.choice([45, 60, 90])  # Medium jobs
        else:  # P_C
            duration = random.choice([60, 90, 120])  # Longer jobs
        
        # Priority (rush or normal)
        is_rush = random.random() < rush_probability
        priority = JobPriority.RUSH if is_rush else JobPriority.NORMAL
        
        # Deadline - rush jobs get tighter deadlines
        if is_rush:
            # Rush: 2-4 hours from shift start
            due_offset = random.randint(120, 240)
        else:
            # Normal: 4-7 hours from shift start
            due_offset = random.randint(240, 420)
        deadline = (base_time + timedelta(minutes=due_offset)).strftime("%H:%M")
        
        # Compatible machines - based on product type and machine capabilities
        compatible_machines = [m_id for m_id, caps in MACHINE_CAPABILITIES.items() if product in caps]
        
        # Sometimes restrict to subset for complexity
        if len(compatible_machines) > 2 and random.random() < 0.3:
            compatible_machines = random.sample(compatible_machines, random.randint(1, 2))
        
        job = Job(
            job_id=job_id,
            product_type=product,
            machine_options=compatible_machines,
            processing_time=duration,
            due_time=deadline,
            priority=priority
        )
        jobs.append(job)
    
    # Sort to make output more organized (for display)
    jobs.sort(key=lambda x: (0 if x.priority == JobPriority.RUSH else 1, x.due_time, x.job_id))
    
    return jobs

def generate_random_downtime(count: int = 1, num_machines: int = 4) -> List[MachineDowntime]:
    """
    Generate random machine downtime events for pharma production.
    """
    downtimes = []
    # Generate machine list dynamically
    machines = [f"M{i+1}" for i in range(num_machines)]
    
    # Generate requested number of downtime events
    for _ in range(count):
        machine = random.choice(machines)
        # Random start between 9 AM and 2 PM
        start_hour = random.randint(9, 14)
        start_min = random.choice([0, 15, 30, 45])
        duration = random.randint(30, 90)
        
        start_dt = datetime.now().replace(hour=start_hour, minute=start_min, second=0)
        end_dt = start_dt + timedelta(minutes=duration)
        
        downtimes.append(MachineDowntime(
            machine_id=machine,
            start_time=start_dt.strftime("%H:%M"),
            end_time=end_dt.strftime("%H:%M"),
            reason=random.choice(["Maintenance", "Equipment Cleaning", "Quality Calibration", "Sterilization"])
        ))
    return downtimes
