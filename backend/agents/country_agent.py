import json
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class CountryAgent(BaseAgent):
    """
    Country Agent responsible for:
    1. Deep analysis of specific country's capabilities for raw material sourcing
    2. Coordinating with expert agents for specialized analysis
    3. Synthesizing expert insights into clear country-specific recommendations
    """
    
    def __init__(self, country_name: str):
        role = f"Expert of country: {country_name}"
        goal = f"Delegate tasks to expert agents and synthesize their output to provide clear values on cost, stability and eco-friendly score for {country_name}"
        
        super().__init__(role, goal)
        self.country_name = country_name
        self.analysis_depth = "comprehensive"
        self.expert_fields = ["eco-friendly", "profitability", "stability"]
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate inputs for country agent"""
        raw_material = kwargs.get("raw_material", "")
        if not raw_material:
            logger.error("raw_material is required for country analysis")
            return False
        
        if not self.country_name:
            logger.error("country_name is required")
            return False
        
        return True
    
    async def conduct_country_research(self, raw_material: str, 
                                     destination_country: str) -> Dict[str, Any]:
        """Conduct comprehensive research on the country's capabilities"""
        logger.info(f"Conducting research on {self.country_name} for {raw_material}")
        
        # Step 1: General country and raw material research
        search_queries = [
            f"{self.country_name} {raw_material} production statistics export volume",
            f"{self.country_name} {raw_material} quality standards certification",
            f"{self.country_name} trade relationship {destination_country} import export",
            f"{self.country_name} economic indicators political stability business environment"
        ]
        
        research_results = {}
        for i, query in enumerate(search_queries):
            search_result = await self.use_tool("duckduckgo", {
                "query": query,
                "max_results": 5
            })
            research_results[f"research_{i+1}"] = {
                "query": query,
                "results": search_result
            }
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        self.store_memory("research_results", research_results, "research")
        
        # Step 2: Compile research summary
        research_summary = await self._compile_research_summary(research_results, raw_material)
        
        return {
            "detailed_research": research_results,
            "research_summary": research_summary,
            "research_timestamp": self.start_time.isoformat() if self.start_time else None
        }
    
    async def _compile_research_summary(self, research_results: Dict[str, Any], 
                                       raw_material: str) -> str:
        """Compile research results into a comprehensive summary"""
        # Combine all research results
        all_research = "\n\n".join([
            f"Query: {result['query']}\nResults: {result['results']}"
            for result in research_results.values()
        ])
        
        claude_prompt = f"""
        Based on the following research data about {self.country_name} and {raw_material}, 
        provide a comprehensive summary covering:
        
        1. Production Capabilities:
           - Current production volume and capacity
           - Quality standards and certifications
           - Infrastructure and logistics
        
        2. Economic Factors:
           - Production costs and pricing
           - Economic stability and growth trends
           - Currency stability and exchange rates
        
        3. Trade Environment:
           - Export experience and capabilities
           - Trade relationships and agreements
           - Regulatory environment
        
        4. Sustainability Factors:
           - Environmental practices
           - Social responsibility
           - Sustainability certifications
        
        5. Risk Assessment:
           - Political risks
           - Economic risks
           - Operational risks
        
        Research Data:
        {all_research}
        
        Provide a structured analysis that will help in making sourcing decisions.
        """
        
        summary = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 2000,
            "temperature": 0.3
        })
        
        self.store_memory("research_summary", summary, "analysis")
        return summary
    
    async def coordinate_expert_analysis(self, raw_material: str, 
                                       destination_country: str) -> Dict[str, Any]:
        """Coordinate with expert agents for specialized analysis"""
        logger.info(f"Coordinating expert analysis for {self.country_name}")
        
        # Import expert agent here to avoid circular imports
        from .expert_agent import ExpertAgent
        
        expert_results = {}
        expert_agents = {}
        
        # Create and execute expert agents
        for field in self.expert_fields:
            logger.info(f"Initiating {field} expert analysis")
            
            expert_agent = ExpertAgent(field)
            expert_agents[field] = expert_agent
            
            try:
                expert_result = await expert_agent.run(
                    raw_material=raw_material,
                    country=self.country_name,
                    destination_country=destination_country
                )
                
                expert_results[field] = expert_result
                logger.info(f"✅ {field} expert analysis completed")
                
            except Exception as e:
                logger.error(f"❌ {field} expert analysis failed: {e}")
                expert_results[field] = {
                    "status": "failed",
                    "error": str(e),
                    "expert_score": 5.0  # Default neutral score
                }
        
        self.store_memory("expert_results", expert_results, "expert_analysis")
        
        return {
            "expert_analyses": expert_results,
            "expert_coordination_summary": self._summarize_expert_coordination(expert_results)
        }
    
    def _summarize_expert_coordination(self, expert_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the coordination with expert agents"""
        successful_experts = []
        failed_experts = []
        expert_scores = {}
        
        for field, result in expert_results.items():
            if result.get("status") == "failed":
                failed_experts.append(field)
            else:
                successful_experts.append(field)
                # Extract expert score from result
                if isinstance(result, dict) and "expert_score" in result:
                    expert_scores[field] = result["expert_score"]
                elif isinstance(result, dict) and "execution_metadata" not in result:
                    # Look for score in nested structure
                    for key, value in result.items():
                        if isinstance(value, dict) and "expert_score" in value:
                            expert_scores[field] = value["expert_score"]
                            break
        
        return {
            "total_experts": len(self.expert_fields),
            "successful_experts": successful_experts,
            "failed_experts": failed_experts,
            "expert_scores": expert_scores,
            "coordination_success_rate": len(successful_experts) / len(self.expert_fields) * 100
        }
    
    def synthesize_country_analysis(self, research_data: Dict[str, Any], 
                                   expert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research and expert analysis into final country assessment"""
        logger.info(f"Synthesizing analysis for {self.country_name}")
        
        # Extract expert scores
        expert_scores = expert_data["expert_coordination_summary"]["expert_scores"]
        
        # Generate derived scores based on analysis
        derived_scores = self._generate_derived_scores(research_data, expert_scores)
        
        # Create comprehensive assessment
        assessment = {
            "country_scores": derived_scores,
            "expert_validation": expert_scores,
            "score_analysis": self._analyze_score_patterns(derived_scores, expert_scores),
            "strengths": self._identify_strengths(derived_scores, expert_scores),
            "weaknesses": self._identify_weaknesses(derived_scores, expert_scores),
            "recommendations": self._generate_country_recommendations(derived_scores, expert_scores)
        }
        
        self.store_memory("country_assessment", assessment, "final_analysis")
        
        return assessment
    
    def _generate_derived_scores(self, research_data: Dict[str, Any], 
                               expert_scores: Dict[str, float]) -> Dict[str, float]:
        """Generate numerical scores based on research and expert analysis"""
        # Base scores (can be enhanced with NLP analysis of research summary)
        base_scores = {
            "cost_score": 7.0,
            "stability_score": 6.5,
            "eco_friendly_score": 7.0
        }
        
        # Adjust based on expert scores
        if "profitability" in expert_scores:
            base_scores["cost_score"] = (base_scores["cost_score"] + expert_scores["profitability"]) / 2
        
        if "stability" in expert_scores:
            base_scores["stability_score"] = (base_scores["stability_score"] + expert_scores["stability"]) / 2
        
        if "eco-friendly" in expert_scores:
            base_scores["eco_friendly_score"] = (base_scores["eco_friendly_score"] + expert_scores["eco-friendly"]) / 2
        
        # Apply research-based adjustments
        research_summary = research_data.get("research_summary", "").lower()
        
        # Cost adjustments
        if any(word in research_summary for word in ["expensive", "high cost", "costly"]):
            base_scores["cost_score"] -= 0.5
        elif any(word in research_summary for word in ["cheap", "low cost", "affordable"]):
            base_scores["cost_score"] += 0.5
        
        # Stability adjustments
        if any(word in research_summary for word in ["unstable", "conflict", "crisis"]):
            base_scores["stability_score"] -= 1.0
        elif any(word in research_summary for word in ["stable", "peaceful", "developed"]):
            base_scores["stability_score"] += 0.5
        
        # Eco-friendly adjustments
        if any(word in research_summary for word in ["sustainable", "green", "eco-friendly"]):
            base_scores["eco_friendly_score"] += 0.5
        elif any(word in research_summary for word in ["pollution", "environmental damage"]):
            base_scores["eco_friendly_score"] -= 0.5
        
        # Ensure scores are within valid range
        for key in base_scores:
            base_scores[key] = max(1.0, min(10.0, base_scores[key]))
            base_scores[key] = round(base_scores[key], 1)
        
        return base_scores
    
    def _analyze_score_patterns(self, derived_scores: Dict[str, float], 
                               expert_scores: Dict[str, float]) -> Dict[str, Any]:
        """Analyze patterns in the scoring data"""
        # Calculate averages
        avg_derived = sum(derived_scores.values()) / len(derived_scores)
        avg_expert = sum(expert_scores.values()) / len(expert_scores) if expert_scores else 0
        
        # Find highest and lowest scores
        highest_derived = max(derived_scores.items(), key=lambda x: x[1])
        lowest_derived = min(derived_scores.items(), key=lambda x: x[1])
        
        # Calculate score variance
        derived_variance = sum((score - avg_derived) ** 2 for score in derived_scores.values()) / len(derived_scores)
        
        return {
            "average_derived_score": round(avg_derived, 2),
            "average_expert_score": round(avg_expert, 2),
            "highest_scoring_area": highest_derived,
            "lowest_scoring_area": lowest_derived,
            "score_variance": round(derived_variance, 2),
            "score_consistency": "high" if derived_variance < 1.0 else "moderate" if derived_variance < 2.0 else "low"
        }
    
    def _identify_strengths(self, derived_scores: Dict[str, float], 
                           expert_scores: Dict[str, float]) -> List[str]:
        """Identify country strengths based on scores"""
        strengths = []
        
        # Check derived scores
        for area, score in derived_scores.items():
            if score >= 8.0:
                area_name = area.replace("_score", "").replace("_", " ").title()
                strengths.append(f"Excellent {area_name} ({score}/10)")
            elif score >= 7.0:
                area_name = area.replace("_score", "").replace("_", " ").title()
                strengths.append(f"Good {area_name} ({score}/10)")
        
        # Check expert validations
        for field, score in expert_scores.items():
            if score >= 8.0:
                strengths.append(f"Expert-validated {field} excellence ({score}/10)")
        
        return strengths if strengths else ["Moderate performance across key areas"]
    
    def _identify_weaknesses(self, derived_scores: Dict[str, float], 
                            expert_scores: Dict[str, float]) -> List[str]:
        """Identify country weaknesses based on scores"""
        weaknesses = []
        
        # Check derived scores
        for area, score in derived_scores.items():
            if score < 6.0:
                area_name = area.replace("_score", "").replace("_", " ").title()
                weaknesses.append(f"Concerning {area_name} ({score}/10)")
            elif score < 7.0:
                area_name = area.replace("_score", "").replace("_", " ").title()
                weaknesses.append(f"Below-average {area_name} ({score}/10)")
        
        # Check expert concerns
        for field, score in expert_scores.items():
            if score < 6.0:
                weaknesses.append(f"Expert-identified {field} concerns ({score}/10)")
        
        return weaknesses if weaknesses else ["No significant weaknesses identified"]
    
    def _generate_country_recommendations(self, derived_scores: Dict[str, float], 
                                        expert_scores: Dict[str, float]) -> List[str]:
        """Generate specific recommendations for this country"""
        recommendations = []
        
        avg_score = sum(derived_scores.values()) / len(derived_scores)
        
        if avg_score >= 8.0:
            recommendations.append("Highly recommended for immediate sourcing consideration")
            recommendations.append("Establish direct relationships with top suppliers")
        elif avg_score >= 7.0:
            recommendations.append("Recommended with standard due diligence procedures")
            recommendations.append("Consider pilot program before full-scale sourcing")
        elif avg_score >= 6.0:
            recommendations.append("Proceed with enhanced risk management protocols")
            recommendations.append("Implement comprehensive supplier auditing")
        else:
            recommendations.append("Consider alternative countries or significant risk mitigation")
            recommendations.append("Require extensive on-ground assessment before proceeding")
        
        # Add specific recommendations based on weak areas
        if derived_scores.get("cost_score", 0) < 6.5:
            recommendations.append("Negotiate volume-based pricing agreements")
        
        if derived_scores.get("stability_score", 0) < 6.5:
            recommendations.append("Implement political risk insurance")
        
        if derived_scores.get("eco_friendly_score", 0) < 6.5:
            recommendations.append("Partner with certified sustainable suppliers")
        
        return recommendations
    
    async def store_country_analysis(self, complete_analysis: Dict[str, Any], 
                                   raw_material: str) -> None:
        """Store the complete country analysis in database"""
        try:
            insert_query = """
            INSERT INTO country_analysis 
            (country, raw_material, search_data, claude_analysis, timestamp) 
            VALUES (%s, %s, %s, %s, NOW())
            """
            
            # Prepare data for storage
            search_data = json.dumps(complete_analysis.get("research_data", {}))[:2000]
            claude_analysis = json.dumps(complete_analysis.get("country_assessment", {}))[:2000]
            
            await self.use_tool("mysql", {
                "query": insert_query,
                "params": [self.country_name, raw_material, search_data, claude_analysis]
            })
            
            logger.info(f"Stored country analysis for {self.country_name} in database")
            
        except Exception as e:
            logger.error(f"Failed to store country analysis: {e}")
    
    async def execute_task(self, **kwargs) -> Dict[str, Any]:
        """Execute the complete country agent task"""
        raw_material = kwargs.get("raw_material", "")
        destination_country = kwargs.get("destination_country", "USA")
        
        logger.info(f"🌍 Country Agent executing analysis for {self.country_name}")
        
        try:
            # Step 1: Conduct comprehensive research
            research_data = await self.conduct_country_research(raw_material, destination_country)
            
            # Step 2: Coordinate with expert agents
            expert_data = await self.coordinate_expert_analysis(raw_material, destination_country)
            
            # Step 3: Synthesize analysis
            country_assessment = self.synthesize_country_analysis(research_data, expert_data)
            
            # Step 4: Store analysis
            complete_analysis = {
                "country": self.country_name,
                "raw_material": raw_material,
                "destination_country": destination_country,
                "research_data": research_data,
                "expert_data": expert_data,
                "country_assessment": country_assessment
            }
            
            await self.store_country_analysis(complete_analysis, raw_material)
            
            logger.info(f"✅ Country Agent completed analysis for {self.country_name}")
            
            return complete_analysis
            
        except Exception as e:
            logger.error(f"Country Agent execution failed for {self.country_name}: {e}")
            raise