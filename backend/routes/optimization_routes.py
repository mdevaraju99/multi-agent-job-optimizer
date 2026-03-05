from fastapi import APIRouter, HTTPException
from models.schemas import OptimizationRequest, AgentResult, ComparisonResponse
from agents.baseline_agent import BaselineAgent
from agents.batching_agent import BatchingAgent
from agents.bottleneck_agent import BottleneckAgent
from agents.orchestrator import OrchestratorAgent

router = APIRouter(prefix="/optimize", tags=["Optimization"])

# Instantiate agents once (or per request if stateful, but here they are stateless mostly)
baseline_agent = BaselineAgent()
batching_agent = BatchingAgent()
bottleneck_agent = BottleneckAgent()
orchestrator_agent = OrchestratorAgent()

@router.post("/baseline", response_model=AgentResult)
async def run_baseline(request: OptimizationRequest):
    return await baseline_agent.optimize(request.jobs, request.downtimes, request.shift)

@router.post("/batching", response_model=AgentResult)
async def run_batching(request: OptimizationRequest):
    return await batching_agent.optimize(request.jobs, request.downtimes, request.shift)

@router.post("/bottleneck", response_model=AgentResult)
async def run_bottleneck(request: OptimizationRequest):
    return await bottleneck_agent.optimize(request.jobs, request.downtimes, request.shift)

@router.post("/orchestrated", response_model=AgentResult)
async def run_orchestrated(request: OptimizationRequest):
    return await orchestrator_agent.optimize(request.jobs, request.downtimes, request.shift)

@router.post("/compare-all", response_model=ComparisonResponse)
async def run_comparison(request: OptimizationRequest):
    return await orchestrator_agent.compare_all(request.jobs, request.downtimes, request.shift)
