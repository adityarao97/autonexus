import json
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class MaterialAnalystAgent(BaseAgent):
    """
    Material Analyst Agent responsible for:
    1. Analyzing final products to identify key raw materials
    2. Determining material importance and priority
    3. Providing detailed material composition analysis
    4. Identifying critical materials for supply chain optimization
    """
    
    def __init__(self, final_product: str):
        role = f"Material Analyst for final product: {final_product}"
        goal = f"Identify and analyze the key raw materials required for manufacturing {final_product}, prioritize them by importance, and provide comprehensive material composition insights"
        
        super().__init__(role, goal)
        self.final_product = final_product
        self.material_knowledge_base = self._load_material_knowledge_base()
        self.analysis_frameworks = self._define_analysis_frameworks()
    
    def _load_material_knowledge_base(self) -> Dict[str, Any]:
        """Load comprehensive knowledge base for material analysis"""
        return {
            # Food Products
            "chocolate": {
                "primary_materials": ["cocoa beans", "sugar", "milk"],
                "secondary_materials": ["cocoa butter", "vanilla", "lecithin"],
                "material_percentages": {"cocoa beans": 40, "sugar": 35, "milk": 20, "others": 5},
                "critical_factors": ["cocoa quality", "sugar purity", "milk fat content"],
                "supply_chain_complexity": "HIGH",
                "seasonal_dependency": "MEDIUM"
            },
            "coffee": {
                "primary_materials": ["coffee beans", "water"],
                "secondary_materials": ["filters", "packaging"],
                "material_percentages": {"coffee beans": 95, "packaging": 3, "others": 2},
                "critical_factors": ["bean quality", "roasting consistency", "freshness"],
                "supply_chain_complexity": "HIGH",
                "seasonal_dependency": "HIGH"
            },
            "bread": {
                "primary_materials": ["wheat flour", "water", "yeast"],
                "secondary_materials": ["salt", "sugar", "oil"],
                "material_percentages": {"wheat flour": 60, "water": 30, "yeast": 3, "others": 7},
                "critical_factors": ["flour quality", "gluten content", "yeast viability"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "LOW"
            },
            "cheese": {
                "primary_materials": ["milk", "rennet", "salt"],
                "secondary_materials": ["cultures", "calcium chloride", "packaging"],
                "material_percentages": {"milk": 85, "salt": 2, "rennet": 1, "others": 12},
                "critical_factors": ["milk quality", "fat content", "bacterial cultures"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "MEDIUM"
            },
            "wine": {
                "primary_materials": ["grapes", "yeast"],
                "secondary_materials": ["sulfites", "fining agents", "bottles"],
                "material_percentages": {"grapes": 90, "yeast": 1, "bottles": 5, "others": 4},
                "critical_factors": ["grape variety", "harvest timing", "fermentation control"],
                "supply_chain_complexity": "HIGH",
                "seasonal_dependency": "VERY_HIGH"
            },
            
            # Textile Products
            "cotton_fabric": {
                "primary_materials": ["cotton fiber", "dyes"],
                "secondary_materials": ["chemicals", "water", "finishing agents"],
                "material_percentages": {"cotton fiber": 80, "dyes": 10, "chemicals": 8, "others": 2},
                "critical_factors": ["fiber quality", "color fastness", "chemical safety"],
                "supply_chain_complexity": "HIGH",
                "seasonal_dependency": "HIGH"
            },
            "wool_fabric": {
                "primary_materials": ["wool fiber", "dyes"],
                "secondary_materials": ["chemicals", "treatments", "finishing"],
                "material_percentages": {"wool fiber": 85, "dyes": 8, "chemicals": 5, "others": 2},
                "critical_factors": ["wool grade", "lanolin content", "fiber length"],
                "supply_chain_complexity": "HIGH",
                "seasonal_dependency": "MEDIUM"
            },
            
            # Paper Products
            "paper": {
                "primary_materials": ["wood pulp", "water", "chemicals"],
                "secondary_materials": ["bleach", "fillers", "coatings"],
                "material_percentages": {"wood pulp": 70, "water": 20, "chemicals": 8, "others": 2},
                "critical_factors": ["pulp quality", "fiber length", "chemical purity"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "LOW"
            },
            
            # Personal Care Products
            "soap": {
                "primary_materials": ["oils", "sodium hydroxide", "water"],
                "secondary_materials": ["fragrances", "colorants", "preservatives"],
                "material_percentages": {"oils": 60, "sodium hydroxide": 15, "water": 20, "others": 5},
                "critical_factors": ["oil quality", "saponification rate", "pH balance"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "LOW"
            },
            "shampoo": {
                "primary_materials": ["surfactants", "water", "conditioning agents"],
                "secondary_materials": ["fragrances", "preservatives", "thickeners"],
                "material_percentages": {"water": 60, "surfactants": 25, "conditioning_agents": 10, "others": 5},
                "critical_factors": ["surfactant quality", "pH stability", "preservation"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "LOW"
            },
            
            # Electronics (simplified)
            "smartphone": {
                "primary_materials": ["silicon", "rare earth metals", "plastics"],
                "secondary_materials": ["glass", "metals", "battery materials"],
                "material_percentages": {"silicon": 30, "metals": 25, "plastics": 20, "others": 25},
                "critical_factors": ["semiconductor purity", "metal conductivity", "material durability"],
                "supply_chain_complexity": "VERY_HIGH",
                "seasonal_dependency": "LOW"
            },
            "laptop": {
                "primary_materials": ["silicon", "aluminum", "plastics"],
                "secondary_materials": ["rare earth metals", "glass", "battery materials"],
                "material_percentages": {"silicon": 25, "metals": 30, "plastics": 25, "others": 20},
                "critical_factors": ["processor quality", "thermal management", "durability"],
                "supply_chain_complexity": "VERY_HIGH",
                "seasonal_dependency": "LOW"
            },
            
            # Construction Materials
            "cement": {
                "primary_materials": ["limestone", "clay", "iron ore"],
                "secondary_materials": ["gypsum", "additives"],
                "material_percentages": {"limestone": 80, "clay": 15, "iron_ore": 3, "others": 2},
                "critical_factors": ["limestone purity", "grinding fineness", "chemical composition"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "LOW"
            },
            
            # Beverages
            "beer": {
                "primary_materials": ["barley", "hops", "yeast"],
                "secondary_materials": ["water", "additives", "packaging"],
                "material_percentages": {"barley": 70, "water": 25, "hops": 2, "others": 3},
                "critical_factors": ["malt quality", "hop freshness", "water purity"],
                "supply_chain_complexity": "MEDIUM",
                "seasonal_dependency": "HIGH"
            }
        }
    
    def _define_analysis_frameworks(self) -> Dict[str, Any]:
        """Define frameworks for material analysis"""
        return {
            "importance_criteria": {
                "cost_impact": 0.3,      # How much the material affects total cost
                "quality_impact": 0.25,  # How much the material affects final quality
                "availability": 0.2,     # How available/scarce the material is
                "substitutability": 0.15, # How easily the material can be substituted
                "regulatory_impact": 0.1  # Regulatory/compliance considerations
            },
            "complexity_factors": {
                "processing_difficulty": ["simple", "moderate", "complex", "very_complex"],
                "quality_requirements": ["basic", "standard", "high", "critical"],
                "supply_chain_tiers": ["direct", "one_tier", "multi_tier", "complex_network"],
                "geographic_concentration": ["distributed", "regional", "concentrated", "single_source"]
            },
            "priority_matrix": {
                "high_cost_high_quality": "CRITICAL",
                "high_cost_medium_quality": "HIGH",
                "medium_cost_high_quality": "HIGH",
                "medium_cost_medium_quality": "MEDIUM",
                "low_cost_high_quality": "MEDIUM",
                "low_cost_medium_quality": "LOW"
            }
        }
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate inputs for material analyst"""
        final_product = kwargs.get("final_product", self.final_product)
        if not final_product or not isinstance(final_product, str):
            logger.error("Invalid final_product provided")
            return False
        
        max_materials = kwargs.get("max_materials", 3)
        if not isinstance(max_materials, int) or max_materials < 1 or max_materials > 10:
            logger.error("max_materials must be between 1 and 10")
            return False
        
        return True
    
    async def conduct_product_research(self, final_product: str) -> Dict[str, Any]:
        """Conduct comprehensive research on the final product"""
        logger.info(f"Conducting product research for {final_product}")
        
        # Step 1: Search for product composition and manufacturing information
        search_queries = [
            f"{final_product} raw materials composition manufacturing",
            f"{final_product} supply chain materials sourcing ingredients",
            f"{final_product} production process key materials components",
            f"{final_product} manufacturing bill of materials BOM"
        ]
        
        research_results = {}
        for i, query in enumerate(search_queries):
            search_result = await self.use_tool("duckduckgo", {
                "query": query,
                "max_results": 6
            })
            research_results[f"search_{i+1}"] = {
                "query": query,
                "results": search_result,
                "focus": self._categorize_search_focus(query)
            }
            
            # Rate limiting
            await asyncio.sleep(0.3)
        
        self.store_memory("product_research", research_results, "research")
        
        # Step 2: Compile comprehensive research summary
        research_summary = await self._compile_product_research_summary(research_results, final_product)
        
        return {
            "research_results": research_results,
            "research_summary": research_summary,
            "research_quality": self._assess_research_quality(research_results)
        }
    
    def _categorize_search_focus(self, query: str) -> str:
        """Categorize the focus area of a search query"""
        query_lower = query.lower()
        
        if "composition" in query_lower or "ingredients" in query_lower:
            return "composition_analysis"
        elif "supply chain" in query_lower or "sourcing" in query_lower:
            return "supply_chain_mapping"
        elif "production" in query_lower or "process" in query_lower:
            return "manufacturing_process"
        elif "bom" in query_lower or "materials" in query_lower:
            return "bill_of_materials"
        else:
            return "general_research"
    
    async def _compile_product_research_summary(self, research_results: Dict[str, Any], 
                                              final_product: str) -> str:
        """Compile research results into a comprehensive summary"""
        # Combine all research results
        all_research = "\n\n".join([
            f"Focus: {result['focus']}\nQuery: {result['query']}\nResults: {result['results']}"
            for result in research_results.values()
        ])
        
        claude_prompt = f"""
        As a material analyst expert, analyze the following research data about {final_product} and provide a comprehensive summary of its material composition and manufacturing requirements.
        
        Please focus on:
        1. Key Raw Materials:
           - Primary materials (most important by volume/value)
           - Secondary materials (supporting/processing materials)
           - Critical materials (those that significantly impact quality/cost)
        
        2. Material Properties:
           - Quality requirements for each material
           - Processing characteristics
           - Storage and handling requirements
        
        3. Supply Chain Considerations:
           - Geographic concentration of material sources
           - Seasonal availability patterns
           - Market dynamics and pricing factors
        
        4. Manufacturing Dependencies:
           - Critical material specifications
           - Substitution possibilities
           - Quality control requirements
        
        Research Data:
        {all_research}
        
        Provide a structured analysis that will help identify the most important materials for sourcing optimization.
        """
        
        summary = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 2500,
            "temperature": 0.3
        })
        
        self.store_memory("research_summary", summary, "analysis")
        return summary
    
    def _assess_research_quality(self, research_results: Dict[str, Any]) -> str:
        """Assess the quality of research data collected"""
        successful_searches = sum(1 for result in research_results.values() 
                                if "error" not in result.get("results", "").lower())
        
        total_searches = len(research_results)
        success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        if success_rate >= 0.8:
            return "EXCELLENT"
        elif success_rate >= 0.6:
            return "GOOD"
        elif success_rate >= 0.4:
            return "FAIR"
        else:
            return "POOR"
    
    async def identify_raw_materials(self, final_product: str, research_summary: str,
                                   max_materials: int = 3) -> Dict[str, Any]:
        """Identify key raw materials using knowledge base and AI analysis"""
        logger.info(f"Identifying raw materials for {final_product}")
        
        # Step 1: Check knowledge base for known product
        known_materials = self._get_known_materials(final_product)
        
        # Step 2: Use Claude for intelligent material identification
        ai_materials = await self._ai_material_identification(final_product, research_summary, max_materials)
        
        # Step 3: Combine and validate materials
        identified_materials = self._combine_and_validate_materials(
            known_materials, ai_materials, max_materials
        )
        
        # Step 4: Generate material analysis
        material_analysis = await self._analyze_identified_materials(
            final_product, identified_materials, research_summary
        )
        
        return {
            "identified_materials": identified_materials,
            "material_analysis": material_analysis,
            "identification_method": "hybrid_knowledge_ai",
            "confidence_score": self._calculate_identification_confidence(known_materials, ai_materials)
        }
    
    def _get_known_materials(self, final_product: str) -> Dict[str, Any]:
        """Get materials from knowledge base if product is known"""
        product_lower = final_product.lower()
        
        # Direct match
        if product_lower in self.material_knowledge_base:
            return self.material_knowledge_base[product_lower]
        
        # Partial match
        for known_product, data in self.material_knowledge_base.items():
            if known_product in product_lower or any(word in product_lower for word in known_product.split()):
                return data
        
        return {}
    
    async def _ai_material_identification(self, final_product: str, research_summary: str,
                                        max_materials: int) -> List[str]:
        """Use AI to identify materials from research"""
        claude_prompt = f"""
        Based on the research summary below, identify the {max_materials} most important raw materials for manufacturing {final_product}.
        
        Consider these criteria for material importance:
        1. Cost impact (materials that significantly affect total production cost)
        2. Quality impact (materials that critically affect final product quality)
        3. Availability (materials that are difficult to source or have limited suppliers)
        4. Processing requirements (materials that require special handling/processing)
        
        Research Summary:
        {research_summary}
        
        Provide your response in this exact JSON format:
        {{
            "materials": ["material1", "material2", "material3"],
            "reasoning": {{
                "material1": "Brief reason why this material is important",
                "material2": "Brief reason why this material is important", 
                "material3": "Brief reason why this material is important"
            }}
        }}
        
        Focus on raw materials, not finished components. For example, for chocolate, identify "cocoa beans" not "chocolate chips".
        """
        
        ai_response = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 1500,
            "temperature": 0.2
        })
        
        return self._extract_materials_from_ai_response(ai_response)
    
    def _extract_materials_from_ai_response(self, ai_response: str) -> List[str]:
        """Extract materials list from AI response"""
        try:
            # Try to parse JSON response
            if "{" in ai_response and "}" in ai_response:
                json_start = ai_response.find("{")
                json_end = ai_response.rfind("}") + 1
                json_str = ai_response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                if "materials" in parsed_data and isinstance(parsed_data["materials"], list):
                    return parsed_data["materials"]
            
            # Fallback: extract from text
            materials = []
            lines = ai_response.split('\n')
            for line in lines:
                # Look for bullet points or numbered lists
                if re.match(r'^\s*[\d\-\*•]\s*([a-zA-Z\s]+)', line):
                    material = re.sub(r'^\s*[\d\-\*•]\s*', '', line).strip()
                    if material and len(material) > 2:
                        materials.append(material.lower())
                        if len(materials) >= 3:
                            break
            
            return materials if materials else ["primary material", "secondary material", "additives"]
            
        except Exception as e:
            logger.error(f"Error extracting materials from AI response: {e}")
            return ["primary material", "secondary material", "additives"]
    
    def _combine_and_validate_materials(self, known_materials: Dict[str, Any], 
                                      ai_materials: List[str], max_materials: int) -> List[str]:
        """Combine knowledge base and AI-identified materials"""
        combined_materials = []
        
        # Priority 1: Known primary materials
        if known_materials and "primary_materials" in known_materials:
            for material in known_materials["primary_materials"][:max_materials]:
                if material not in combined_materials:
                    combined_materials.append(material)
        
        # Priority 2: AI-identified materials
        for material in ai_materials:
            if len(combined_materials) >= max_materials:
                break
            if material not in combined_materials:
                combined_materials.append(material)
        
        # Priority 3: Known secondary materials if still need more
        if len(combined_materials) < max_materials and known_materials and "secondary_materials" in known_materials:
            for material in known_materials["secondary_materials"]:
                if len(combined_materials) >= max_materials:
                    break
                if material not in combined_materials:
                    combined_materials.append(material)
        
        # Ensure we have the requested number of materials
        while len(combined_materials) < max_materials:
            combined_materials.append(f"material_{len(combined_materials) + 1}")
        
        return combined_materials[:max_materials]
    
    async def _analyze_identified_materials(self, final_product: str, materials: List[str],
                                          research_summary: str) -> Dict[str, Any]:
        """Perform detailed analysis of identified materials"""
        material_details = {}
        
        for material in materials:
            # Get known data if available
            known_data = self._get_material_known_data(final_product, material)
            
            # Generate detailed analysis
            analysis = await self._generate_material_analysis(material, final_product, research_summary)
            
            material_details[material] = {
                "importance_score": self._calculate_material_importance(material, known_data, analysis),
                "cost_impact": known_data.get("cost_impact", "MEDIUM"),
                "quality_impact": known_data.get("quality_impact", "MEDIUM"),
                "supply_complexity": known_data.get("supply_complexity", "MEDIUM"),
                "substitutability": known_data.get("substitutability", "MEDIUM"),
                "seasonal_dependency": known_data.get("seasonal_dependency", "LOW"),
                "detailed_analysis": analysis,
                "sourcing_priority": self._calculate_sourcing_priority(material, known_data)
            }
        
        return material_details
    
    def _get_material_known_data(self, final_product: str, material: str) -> Dict[str, Any]:
        """Get known data about a specific material for the product"""
        known_materials = self._get_known_materials(final_product)
        
        if not known_materials:
            return {}
        
        # Check if material is in primary or secondary lists
        material_lower = material.lower()
        
        if "primary_materials" in known_materials:
            if material_lower in [m.lower() for m in known_materials["primary_materials"]]:
                return {
                    "cost_impact": "HIGH",
                    "quality_impact": "HIGH",
                    "supply_complexity": known_materials.get("supply_chain_complexity", "MEDIUM"),
                    "substitutability": "LOW",
                    "seasonal_dependency": known_materials.get("seasonal_dependency", "MEDIUM")
                }
        
        if "secondary_materials" in known_materials:
            if material_lower in [m.lower() for m in known_materials["secondary_materials"]]:
                return {
                    "cost_impact": "MEDIUM",
                    "quality_impact": "MEDIUM", 
                    "supply_complexity": "MEDIUM",
                    "substitutability": "MEDIUM",
                    "seasonal_dependency": "LOW"
                }
        
        return {}
    
    async def _generate_material_analysis(self, material: str, final_product: str,
                                        research_summary: str) -> str:
        """Generate detailed analysis for a specific material"""
        claude_prompt = f"""
        As a material sourcing expert, provide a detailed analysis of {material} as a key raw material for {final_product} manufacturing.
        
        Based on the research summary provided, analyze:
        
        1. Material Characteristics:
           - Quality specifications and standards
           - Processing requirements
           - Storage and handling needs
        
        2. Supply Market Analysis:
           - Major producing regions/countries
           - Market concentration and competition
           - Price volatility and trends
        
        3. Sourcing Challenges:
           - Quality consistency issues
           - Seasonal availability
           - Transportation requirements
           - Regulatory considerations
        
        4. Strategic Importance:
           - Impact on final product quality
           - Cost significance in overall product
           - Substitution possibilities and limitations
        
        Research Context:
        {research_summary}
        
        Provide specific, actionable insights that will help in sourcing strategy development.
        """
        
        analysis = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 1500,
            "temperature": 0.3
        })
        
        return analysis
    
    def _calculate_material_importance(self, material: str, known_data: Dict[str, Any],
                                     analysis: str) -> float:
        """Calculate overall importance score for a material"""
        # Base score
        base_score = 5.0
        
        # Adjust based on known data
        if known_data.get("cost_impact") == "HIGH":
            base_score += 1.5
        elif known_data.get("cost_impact") == "MEDIUM":
            base_score += 0.5
        
        if known_data.get("quality_impact") == "HIGH":
            base_score += 1.5
        elif known_data.get("quality_impact") == "MEDIUM":
            base_score += 0.5
        
        if known_data.get("supply_complexity") == "VERY_HIGH":
            base_score += 1.0
        elif known_data.get("supply_complexity") == "HIGH":
            base_score += 0.5
        
        # Adjust based on analysis content
        analysis_lower = analysis.lower()
        
        # Positive indicators
        if any(word in analysis_lower for word in ["critical", "essential", "crucial"]):
            base_score += 0.5
        if any(word in analysis_lower for word in ["high impact", "significant", "major"]):
            base_score += 0.3
        
        # Negative indicators
        if any(word in analysis_lower for word in ["minor", "minimal", "limited impact"]):
            base_score -= 0.5
        
        # Ensure score is within valid range
        return max(1.0, min(10.0, round(base_score, 1)))
    
    def _calculate_sourcing_priority(self, material: str, known_data: Dict[str, Any]) -> str:
        """Calculate sourcing priority for a material"""
        cost_impact = known_data.get("cost_impact", "MEDIUM")
        quality_impact = known_data.get("quality_impact", "MEDIUM")
        
        if cost_impact == "HIGH" and quality_impact == "HIGH":
            return "CRITICAL"
        elif cost_impact == "HIGH" or quality_impact == "HIGH":
            return "HIGH"
        elif cost_impact == "MEDIUM" and quality_impact == "MEDIUM":
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_identification_confidence(self, known_materials: Dict[str, Any],
                                           ai_materials: List[str]) -> float:
        """Calculate confidence in material identification"""
        confidence_factors = 0
        
        # Factor 1: Known product in knowledge base
        if known_materials:
            confidence_factors += 2
        
        # Factor 2: AI identified reasonable materials
        if ai_materials and len(ai_materials) >= 2:
            confidence_factors += 1
        
        # Factor 3: Consistency between known and AI
        if known_materials and ai_materials:
            known_primary = [m.lower() for m in known_materials.get("primary_materials", [])]
            ai_lower = [m.lower() for m in ai_materials]
            
            overlap = len(set(known_primary) & set(ai_lower))
            if overlap >= 1:
                confidence_factors += 1
        
        # Convert to 1-10 scale
        confidence_score = min(10.0, max(1.0, (confidence_factors / 4.0) * 10))
        return round(confidence_score, 1)
    
    async def generate_material_importance_ranking(self, material_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final ranking and importance analysis"""
        logger.info("Generating material importance ranking")
        
        # Sort materials by importance score
        sorted_materials = sorted(
            material_details.items(),
            key=lambda x: x[1]["importance_score"],
            reverse=True
        )
        
        # Generate importance insights
        importance_insights = await self._generate_importance_insights(sorted_materials)
        
        # Create strategic recommendations
        strategic_recommendations = self._create_strategic_recommendations(sorted_materials)
        
        return {
            "material_ranking": [
                {
                    "rank": i + 1,
                    "material": material,
                    "importance_score": details["importance_score"],
                    "sourcing_priority": details["sourcing_priority"],
                    "key_factors": [
                        f"Cost Impact: {details['cost_impact']}",
                        f"Quality Impact: {details['quality_impact']}",
                        f"Supply Complexity: {details['supply_complexity']}"
                    ]
                }
                for i, (material, details) in enumerate(sorted_materials)
            ],
            "importance_insights": importance_insights,
            "strategic_recommendations": strategic_recommendations,
            "overall_complexity": self._assess_overall_complexity(material_details)
        }
    
    async def _generate_importance_insights(self, sorted_materials: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Generate insights about material importance"""
        if not sorted_materials:
            return "No materials identified for analysis."
        
        material_summaries = []
        for material, details in sorted_materials:
            material_summaries.append(
                f"{material}: Importance={details['importance_score']}/10, "
                f"Priority={details['sourcing_priority']}, "
                f"Cost Impact={details['cost_impact']}"
            )
        
        claude_prompt = f"""
        Based on the material analysis results below, provide strategic insights about the material importance hierarchy and sourcing implications.
        
        Material Analysis:
        {chr(10).join(material_summaries)}
        
        Provide insights on:
        1. Critical material dependencies
        2. Risk concentration areas  
        3. Sourcing strategy implications
        4. Supply chain optimization opportunities
        
        Keep the analysis strategic and actionable.
        """
        
        insights = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 1000,
            "temperature": 0.4
        })
        
        return insights
    
    def _create_strategic_recommendations(self, sorted_materials: List[Tuple[str, Dict[str, Any]]]) -> List[str]:
        """Create strategic recommendations based on material analysis"""
        recommendations = []
        
        if not sorted_materials:
            return ["No materials identified - conduct deeper product analysis"]
        
        # Top priority material recommendations
        top_material, top_details = sorted_materials[0]
        if top_details["importance_score"] >= 8.0:
            recommendations.append(f"Prioritize {top_material} sourcing with dedicated supplier management")
        
        if top_details["sourcing_priority"] == "CRITICAL":
            recommendations.append(f"Establish strategic partnerships for {top_material} supply")
        
        # Complexity-based recommendations
        high_complexity_materials = [
            material for material, details in sorted_materials
            if details["supply_complexity"] in ["HIGH", "VERY_HIGH"]
        ]
        
        if high_complexity_materials:
            recommendations.append(f"Develop specialized sourcing strategies for complex materials: {', '.join(high_complexity_materials[:2])}")
        
        # Diversification recommendations
        if len(sorted_materials) >= 3:
            recommendations.append("Implement diversified sourcing strategy across all key materials")
        
        # Risk management recommendations
        seasonal_materials = [
            material for material, details in sorted_materials
            if details["seasonal_dependency"] in ["HIGH", "VERY_HIGH"]
        ]
        
        if seasonal_materials:
            recommendations.append(f"Plan seasonal inventory strategies for: {', '.join(seasonal_materials)}")
        
        return recommendations if recommendations else ["Develop comprehensive material sourcing framework"]
    
    def _assess_overall_complexity(self, material_details: Dict[str, Any]) -> str:
        """Assess overall sourcing complexity"""
        if not material_details:
            return "UNKNOWN"
        
        complexity_scores = []
        for details in material_details.values():
            complexity = details.get("supply_complexity", "MEDIUM")
            if complexity == "VERY_HIGH":
                complexity_scores.append(4)
            elif complexity == "HIGH":
                complexity_scores.append(3)
            elif complexity == "MEDIUM":
                complexity_scores.append(2)
            else:
                complexity_scores.append(1)
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        
        if avg_complexity >= 3.5:
            return "VERY_HIGH"
        elif avg_complexity >= 2.5:
            return "HIGH"
        elif avg_complexity >= 1.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def execute_task(self, **kwargs) -> Dict[str, Any]:
        """Execute the complete material analyst task"""
        final_product = kwargs.get("final_product", self.final_product)
        max_materials = kwargs.get("max_materials", 3)
        
        logger.info(f"🔬 Material Analyst executing analysis for {final_product}")
        
        try:
            # Step 1: Conduct product research
            research_data = await self.conduct_product_research(final_product)
            
            # Step 2: Identify raw materials
            material_identification = await self.identify_raw_materials(
                final_product, research_data["research_summary"], max_materials
            )
            
            # Step 3: Generate importance ranking
            importance_ranking = await self.generate_material_importance_ranking(
                material_identification["material_analysis"]
            )
            
            # Compile complete result
            result = {
                "final_product": final_product,
                "identified_materials": material_identification["identified_materials"],
                "material_analysis": material_identification["material_analysis"],
                "material_importance": importance_ranking,
                "research_quality": research_data["research_quality"],
                "identification_confidence": material_identification["confidence_score"],
                "overall_complexity": importance_ranking["overall_complexity"],
                "strategic_recommendations": importance_ranking["strategic_recommendations"],
                "analysis_summary": {
                    "total_materials_analyzed": len(material_identification["identified_materials"]),
                    "critical_materials": len([
                        m for m in material_identification["material_analysis"].values()
                        if m["sourcing_priority"] == "CRITICAL"
                    ]),
                    "high_priority_materials": len([
                        m for m in material_identification["material_analysis"].values()
                        if m["sourcing_priority"] == "HIGH"
                    ])
                }
            }
            
            logger.info(f"✅ Material Analyst completed analysis for {final_product}")
            logger.info(f"   Identified materials: {material_identification['identified_materials']}")
            logger.info(f"   Overall complexity: {importance_ranking['overall_complexity']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Material Analyst execution failed for {final_product}: {e}")
            raise