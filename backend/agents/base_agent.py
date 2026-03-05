from abc import ABC, abstractmethod
from typing import List
from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def optimize(
        self, 
        jobs: List[Job], 
        downtimes: List[MachineDowntime], 
        constraints: ShiftConstraints
    ) -> AgentResult:
        """
        Run the optimization logic.
        """
        pass
        
    def calculate_setup_time(self, last_product: str, current_product: str) -> int:
        """Standard setup logic: 10 mins if product types differ."""
        if last_product and last_product != current_product:
            return 10
        return 0
        
    def log(self, message: str):
        print(f"[{self.name}] {message}")
