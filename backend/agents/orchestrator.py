import asyncio
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from models.schemas import Job, MachineDowntime, ShiftConstraints, AgentResult, ComparisonResponse
from .base_agent import BaseAgent
from .baseline_agent import BaselineAgent
from .batching_agent import BatchingAgent
from .bottleneck_agent import BottleneckAgent
from .constraint_agent import ConstraintAgent
from config import settings

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orchestrator Agent")
        self.baseline = BaselineAgent()
        self.batching = BatchingAgent()
        self.bottleneck = BottleneckAgent()
        self.constraint = ConstraintAgent()
        
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME
        )

    async def optimize(
        self, 
        jobs: List[Job], 
        downtimes: List[MachineDowntime], 
        constraints: ShiftConstraints
    ) -> AgentResult:
        self.log("Orchestrating all agents...")
        
        # Run all agents in parallel
        results = await asyncio.gather(
            self.baseline.optimize(jobs, downtimes, constraints),
            self.batching.optimize(jobs, downtimes, constraints),
            self.bottleneck.optimize(jobs, downtimes, constraints)
        )
        
        baseline_res, batching_res, bottleneck_res = results
        
        # Validate all schedules
        for res in results:
            res.violations = self.constraint.validate(res.schedules, jobs, downtimes, constraints)
            
        # --- SUPERVISOR AGENT LOGIC ---
        # "Consolidates candidate schedules and chooses the best one using KPI-driven scoring."
        
        candidates = [baseline_res, batching_res, bottleneck_res]
        
        # 1. Scoring & Selection (Supervisor Rules)
        best_agent = None
        best_score = -float('inf')
        
        self.log("Supervisor: Evaluating candidates...")
        
        for cand in candidates:
            # Supervisor Rule: Prioritize Zero Violations
            violation_penalty = len(cand.violations) * 100 
             # Supervisor Rule: Weighted KPI Formula (handled in kpi_calculator, but we adjust for decision)
            final_score = cand.kpis.score - violation_penalty
            
            self.log(f"Candidate {cand.agent_name}: KPI Score={cand.kpis.score:.2f}, Violations={len(cand.violations)}, Final Selection Score={final_score:.2f}")
            
            if final_score > best_score:
                best_score = final_score
                best_agent = cand
        
        # 2. Generate Supervisor Explanation
        # "Generates clear, non-technical explanations for plant managers"
        
        self.log(f"Supervisor: Selected {best_agent.agent_name} as optimal strategy.")
        
        supervisor_explanation = await self._generate_supervisor_explanation(best_agent, candidates)
        
        best_agent.explanation = supervisor_explanation
        return best_agent

    async def compare_all(self, jobs, downtimes, constraints) -> ComparisonResponse:
        results = await asyncio.gather(
            self.baseline.optimize(jobs, downtimes, constraints),
            self.batching.optimize(jobs, downtimes, constraints),
            self.bottleneck.optimize(jobs, downtimes, constraints)
        )
        
        # Validate
        for res in results:
            res.violations = self.constraint.validate(res.schedules, jobs, downtimes, constraints)
            
        # Run Supervisor Selection logic
        best_res = await self.optimize(jobs, downtimes, constraints)
        
        return ComparisonResponse(
            baseline=results[0],
            batching=results[1],
            bottleneck=results[2],
            orchestrated=best_res,
            summary=best_res.explanation
        )

    async def _generate_supervisor_explanation(self, best, candidates):
        try:
            summary = "\n".join([
                f"- {c.agent_name}: Score {c.kpis.score:.1f}, Violations {len(c.violations)}, Setup {c.kpis.total_setup_time}m, Tardiness {c.kpis.total_tardiness}m" 
                for c in candidates
            ])
            
            # Supervisor System Prompt from Architecture Doc
            prompt = ChatPromptTemplate.from_template(
                """
                You are the **Supervisor Agent** for a Pharmaceutical Production Facility.
                Your role is to coordinate specialist agents and select the best schedule for the plant managers.
                
                **Candidates Evaluated:**
                {summary}
                
                **Selected Winner:** {winner} (Reason: Highest Efficiency Score & Lowest Constraint Violations)
                
                **Your Task:**
                Generate a clear, executive-level explanation for why this schedule was chosen.
                
                **Guidelines:**
                1. Start with "As the Supervisor Agent, I have selected..."
                2. Highlight the key benefits (e.g., "Reduced setup time by...", "Zero compliance violations").
                3. Explain why the others were rejected (e.g., "Batching Agent had fewer setups but missed deadlines").
                4. Maintain a professional, reassuring tone ensuring production goals are met.
                5. Mention if any critical constraints (like rush orders or downtime) were handled effectively.
                
                Keep it under 200 words.
                """
            )
            chain = prompt | self.llm
            res = await chain.ainvoke({
                "summary": summary,
                "winner": best.agent_name
            })
            return res.content
        except Exception as e:
            return f"Supervisor Selection: {best.agent_name} was chosen based on the highest weighted score ({best.kpis.score:.2f}) and lowest violations ({len(best.violations)})."

