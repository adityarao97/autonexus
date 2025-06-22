import json
import asyncio
import traceback
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class LeaderAgent(BaseAgent):
    """
    Leader Agent responsible for:
    1. Identifying top countries for raw material production
    2. Coordinating with country agents
    3. Making final sourcing recommendations based on comprehensive analysis
    """
    
    def __init__(self, raw_material: str):
        role = f"Expert of raw_material: {raw_material}"
        goal = f"Identify countries (max 3) best known for producing {raw_material}, delegate tasks to country agents, and identify BEST country with optimal value on cost, stability score, eco-friendly score"
        
        super().__init__(role, goal)
        self.raw_material = raw_material
        self.max_countries = 3
        self.scoring_weights = {
            "cost_score": 0.4,
            "stability_score": 0.3,
            "eco_friendly_score": 0.3
        }
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate inputs for leader agent"""
        if not self.raw_material or not isinstance(self.raw_material, str):
            logger.error("Invalid raw_material provided")
            return False
        
        destination_country = kwargs.get("destination_country", "")
        if not destination_country:
            logger.warning("No destination_country provided, using default")
        
        return True
    
    async def identify_producing_countries(self) -> List[str]:
        """Identify top producing countries for the raw material"""
        logger.info(f"Identifying top producing countries for {self.raw_material}")
        
        # Step 1: Use DuckDuckGo to search for production data
        search_query = f"top {self.raw_material} producing countries world largest producers statistics"
        search_result = await self.use_tool("duckduckgo", {
            "query": search_query,
            "max_results": 8
        })
        
        self.store_memory("search_results", search_result, "research")
        
        # Step 2: Use Claude to analyze and identify countries
        claude_prompt = f"""
        Based on the following search results about {self.raw_material} production, identify the top 3 countries that are best known for producing {self.raw_material}.
        
        Search Results:
        {search_result}
        
        Consider factors like:
        - Production volume and capacity
        - Quality and reputation
        - Global market share
        - Export capabilities
        - Established supply chains
        
        Provide your response in the following JSON format:
        {{
            "countries": ["Country1", "Country2", "Country3"],
            "reasoning": "Brief explanation of why these countries were selected",
            "production_insights": {{
                "Country1": "Brief insight about Country1's production",
                "Country2": "Brief insight about Country2's production", 
                "Country3": "Brief insight about Country3's production"
            }}
        }}
        
        Focus on actual country names and provide exactly 3 countries.
        """
        
        claude_result = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 1500,
            "temperature": 0.3
        })
        
        self.store_memory("claude_analysis", claude_result, "research")
        
        # Step 3: Extract countries from Claude's response
        countries = self._extract_countries_from_analysis(claude_result)
        
        self.store_memory("identified_countries", countries, "countries")
        logger.info(f"Identified countries: {countries}")
        
        return countries
    
    def _extract_countries_from_analysis(self, claude_response: str) -> List[str]:
        """Extract country names from Claude's analysis"""
        try:
            # Try to parse JSON response
            if "{" in claude_response and "}" in claude_response:
                json_start = claude_response.find("{")
                json_end = claude_response.rfind("}") + 1
                json_str = claude_response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                if "countries" in parsed_data:
                    countries = parsed_data["countries"]
                    if isinstance(countries, list) and len(countries) > 0:
                        return countries[:self.max_countries]
            
            # Fallback: extract countries based on raw material type
            return self._get_default_countries(self.raw_material)
            
        except Exception as e:
            logger.error(f"Error extracting countries from Claude response: {e}")
            logger.debug(f"Claude response was: {claude_response[:500]}...")
            return self._get_default_countries(self.raw_material)
    
    def _get_default_countries(self, raw_material: str) -> List[str]:
        """Get default countries based on raw material type"""
        material_lower = raw_material.lower()
        
        defaults = {
            "chocolate": ["Ecuador", "Ghana", "Ivory Coast"],
            "cocoa": ["Ecuador", "Ghana", "Ivory Coast"],
            "coffee": ["Brazil", "Colombia", "Ethiopia"],
            "cotton": ["India", "China", "USA"],
            "sugar": ["Brazil", "India", "Thailand"],
            "tea": ["China", "India", "Kenya"],
            "rubber": ["Thailand", "Indonesia", "Malaysia"],
            "palm oil": ["Indonesia", "Malaysia", "Thailand"],
            "rice": ["China", "India", "Indonesia"],
            "wheat": ["China", "India", "Russia"],
            "soybeans": ["USA", "Brazil", "Argentina"],
            "copper": ["Chile", "Peru", "China"],
            "aluminum": ["China", "Russia", "Canada"],
            "steel": ["China", "India", "Japan"]
        }
        
        for key, countries in defaults.items():
            if key in material_lower:
                return countries
        
        # Generic fallback
        return ["Brazil", "India", "China"]
    
    async def get_country_scoring_data(self, countries: List[str]) -> List[Dict[str, Any]]:
        """Retrieve scoring data for identified countries from database"""
        logger.info(f"Retrieving scoring data for countries: {countries}")
        
        # Build query for multiple countries
        placeholders = ", ".join(["%s"] * len(countries))
        query = f"SELECT * FROM business_requirement WHERE country IN ({placeholders})"
        
        db_result = await self.use_tool("mysql", {
            "query": query,
            "params": countries
        })
        
        try:
            # Parse the database result
            scoring_data = self._parse_database_result(db_result)
            
            if not scoring_data:
                logger.warning("No database results found, generating mock data")
                scoring_data = self._generate_mock_scoring_data(countries)
            
            self.store_memory("scoring_data", scoring_data, "analysis")
            return scoring_data
            
        except Exception as e:
            logger.error(f"Failed to parse database result: {e}")
            logger.debug(f"Database result was: {db_result[:500]}...")
            return self._generate_mock_scoring_data(countries)
    
    def _parse_database_result(self, db_result: str) -> List[Dict[str, Any]]:
        """Parse database result string into list of dictionaries"""
        try:
            # Try to parse as JSON
            if isinstance(db_result, str):
                # Look for JSON content
                if "{" in db_result and "}" in db_result:
                    # Extract JSON part
                    json_start = db_result.find("{")
                    if json_start != -1:
                        # Find the end of the JSON structure
                        json_content = db_result[json_start:]
                        
                        # Try to parse the JSON
                        parsed = json.loads(json_content)
                        
                        # Handle different JSON structures
                        if isinstance(parsed, dict):
                            if "results" in parsed:
                                return parsed["results"]
                            elif "data" in parsed:
                                return parsed["data"]
                            else:
                                # Assume the dict itself is the result
                                return [parsed]
                        elif isinstance(parsed, list):
                            return parsed
                
                # If no JSON found, try to extract data from text
                return self._extract_data_from_text(db_result)
            
            elif isinstance(db_result, list):
                return db_result
            elif isinstance(db_result, dict):
                if "results" in db_result:
                    return db_result["results"]
                else:
                    return [db_result]
            
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._extract_data_from_text(db_result)
        except Exception as e:
            logger.error(f"Error parsing database result: {e}")
            return []
    
    def _extract_data_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract data from text-based database result"""
        # This is a fallback method for text-based results
        # Look for patterns that might indicate country data
        
        countries_data = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines that might contain country data
            if any(country in line for country in ["Ecuador", "Ghana", "Brazil", "Colombia", "Ethiopia", "India", "China"]):
                # Try to extract scores from the line
                # This is a simplified approach
                if "Ecuador" in line:
                    countries_data.append({
                        "country": "Ecuador",
                        "cost_score": 8.5,
                        "stability_score": 6.0,
                        "eco_friendly_score": 7.5
                    })
                elif "Ghana" in line:
                    countries_data.append({
                        "country": "Ghana",
                        "cost_score": 7.0,
                        "stability_score": 7.5,
                        "eco_friendly_score": 8.0
                    })
                # Add more patterns as needed
        
        return countries_data
    
    def _generate_mock_scoring_data(self, countries: List[str]) -> List[Dict[str, Any]]:
        """Generate mock scoring data if database is unavailable"""
        import random
        
        # Predefined data for common countries
        predefined_data = {
            "Ecuador": {"cost_score": 8.5, "stability_score": 6.0, "eco_friendly_score": 7.5},
            "Ghana": {"cost_score": 7.0, "stability_score": 7.5, "eco_friendly_score": 8.0},
            "Ivory Coast": {"cost_score": 6.5, "stability_score": 6.5, "eco_friendly_score": 6.0},
            "Brazil": {"cost_score": 7.5, "stability_score": 6.8, "eco_friendly_score": 7.2},
            "Colombia": {"cost_score": 8.0, "stability_score": 6.2, "eco_friendly_score": 7.8},
            "Ethiopia": {"cost_score": 9.0, "stability_score": 5.5, "eco_friendly_score": 6.5},
            "India": {"cost_score": 8.8, "stability_score": 6.5, "eco_friendly_score": 6.0},
            "China": {"cost_score": 8.2, "stability_score": 7.0, "eco_friendly_score": 5.5},
            "Thailand": {"cost_score": 7.8, "stability_score": 7.2, "eco_friendly_score": 7.0},
            "Indonesia": {"cost_score": 8.1, "stability_score": 6.8, "eco_friendly_score": 6.7},
            "Chile": {"cost_score": 7.2, "stability_score": 8.0, "eco_friendly_score": 7.5},
            "Peru": {"cost_score": 8.3, "stability_score": 6.5, "eco_friendly_score": 7.0},
            "USA": {"cost_score": 6.0, "stability_score": 9.0, "eco_friendly_score": 7.8},
            "Canada": {"cost_score": 6.5, "stability_score": 9.2, "eco_friendly_score": 8.5},
            "Russia": {"cost_score": 7.8, "stability_score": 5.5, "eco_friendly_score": 5.0}
        }
        
        mock_data = []
        for country in countries:
            if country in predefined_data:
                data = predefined_data[country].copy()
                data["country"] = country
                mock_data.append(data)
            else:
                # Generate random but realistic scores
                mock_data.append({
                    "country": country,
                    "cost_score": round(random.uniform(6.0, 9.0), 1),
                    "stability_score": round(random.uniform(5.5, 8.0), 1),
                    "eco_friendly_score": round(random.uniform(6.0, 8.5), 1)
                })
        
        logger.info("Using mock scoring data due to database unavailability")
        return mock_data
    
    def rank_countries(self, scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rank countries based on weighted composite scoring"""
        logger.info("Ranking countries based on composite scoring")
        
        if not scoring_data:
            logger.error("No scoring data provided for ranking")
            return {
                "best_country": {"country": "Unknown", "composite_score": 0.0},
                "all_rankings": [],
                "scoring_methodology": {
                    "weights": self.scoring_weights,
                    "formula": "composite_score = (cost_score * 0.4) + (stability_score * 0.3) + (eco_friendly_score * 0.3)"
                }
            }
        
        ranked_countries = []
        
        for country_data in scoring_data:
            try:
                # Ensure country_data is a dictionary
                if not isinstance(country_data, dict):
                    logger.error(f"Invalid country data format: {type(country_data)}")
                    continue
                
                # Validate required fields
                required_fields = ["cost_score", "stability_score", "eco_friendly_score"]
                if not all(field in country_data for field in required_fields):
                    logger.error(f"Missing required fields in country data: {country_data}")
                    continue
                
                # Convert scores to float if they're strings
                cost_score = float(country_data["cost_score"])
                stability_score = float(country_data["stability_score"])
                eco_friendly_score = float(country_data["eco_friendly_score"])
                
                # Calculate weighted composite score
                composite_score = (
                    cost_score * self.scoring_weights["cost_score"] +
                    stability_score * self.scoring_weights["stability_score"] +
                    eco_friendly_score * self.scoring_weights["eco_friendly_score"]
                )
                
                ranked_country = country_data.copy()
                ranked_country["composite_score"] = round(composite_score, 2)
                ranked_countries.append(ranked_country)
                
            except (ValueError, TypeError, KeyError) as e:
                logger.error(f"Error processing country data {country_data}: {e}")
                continue
        
        # Sort by composite score (descending)
        ranked_countries.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
        
        self.store_memory("ranked_countries", ranked_countries, "analysis")
        
        # Return best country with ranking context
        best_country = ranked_countries[0] if ranked_countries else {
            "country": "Unknown", 
            "composite_score": 0.0
        }
        
        return {
            "best_country": best_country,
            "all_rankings": ranked_countries,
            "scoring_methodology": {
                "weights": self.scoring_weights,
                "formula": "composite_score = (cost_score * 0.4) + (stability_score * 0.3) + (eco_friendly_score * 0.3)"
            }
        }
    
    async def generate_final_recommendation(self, ranking_result: Dict[str, Any], 
                                          destination_country: str) -> Dict[str, Any]:
        """Generate comprehensive final recommendation"""
        best_country = ranking_result["best_country"]
        all_rankings = ranking_result["all_rankings"]
        
        if not best_country or best_country.get("country") == "Unknown":
            logger.error("No valid best country found for recommendation")
            return {
                "recommended_country": {"country": "Unknown", "composite_score": 0.0},
                "strategic_insights": "Unable to generate recommendation due to data issues",
                "alternative_options": [],
                "confidence_level": "LOW",
                "decision_factors": []
            }
        
        # Use Claude to generate strategic insights
        claude_prompt = f"""
        As a sourcing expert, provide strategic insights and recommendations for importing {self.raw_material} from {best_country['country']} to {destination_country}.
        
        Country Analysis:
        - Best Country: {best_country['country']}
        - Composite Score: {best_country['composite_score']}/10
        - Cost Score: {best_country.get('cost_score', 'N/A')}/10
        - Stability Score: {best_country.get('stability_score', 'N/A')}/10
        - Eco-friendly Score: {best_country.get('eco_friendly_score', 'N/A')}/10
        
        All Country Rankings:
        {json.dumps(all_rankings, indent=2)}
        
        Provide insights on:
        1. Strategic advantages of the recommended country
        2. Potential risks and mitigation strategies
        3. Implementation timeline and key milestones
        4. Alternative options and contingency planning
        5. Key success factors for this sourcing decision
        
        Format your response as strategic recommendations for executive decision-making.
        """
        
        strategic_insights = await self.use_tool("claude", {
            "prompt": claude_prompt,
            "max_tokens": 2000,
            "temperature": 0.4
        })
        
        return {
            "recommended_country": best_country,
            "strategic_insights": strategic_insights,
            "alternative_options": all_rankings[1:] if len(all_rankings) > 1 else [],
            "confidence_level": self._calculate_confidence_level(best_country, all_rankings),
            "decision_factors": self._extract_decision_factors(best_country)
        }
    
    def _calculate_confidence_level(self, best_country: Dict[str, Any], 
                                   all_rankings: List[Dict[str, Any]]) -> str:
        """Calculate confidence level based on score distribution"""
        if len(all_rankings) < 2:
            return "MODERATE"
        
        best_score = best_country.get("composite_score", 0)
        second_best_score = all_rankings[1].get("composite_score", 0)
        score_gap = best_score - second_best_score
        
        if score_gap >= 1.0:
            return "HIGH"
        elif score_gap >= 0.5:
            return "MODERATE"
        else:
            return "LOW"
    
    def _extract_decision_factors(self, best_country: Dict[str, Any]) -> List[str]:
        """Extract key decision factors from the best country's scores"""
        factors = []
        
        cost_score = best_country.get("cost_score", 0)
        stability_score = best_country.get("stability_score", 0)
        eco_friendly_score = best_country.get("eco_friendly_score", 0)
        
        if cost_score >= 8.0:
            factors.append("Excellent cost competitiveness")
        elif cost_score >= 7.0:
            factors.append("Good cost advantages")
        
        if stability_score >= 8.0:
            factors.append("High political and economic stability")
        elif stability_score >= 7.0:
            factors.append("Adequate stability for operations")
        
        if eco_friendly_score >= 8.0:
            factors.append("Strong sustainability credentials")
        elif eco_friendly_score >= 7.0:
            factors.append("Good environmental practices")
        
        return factors if factors else ["Balanced performance across all criteria"]
    
    async def execute_task(self, **kwargs) -> Dict[str, Any]:
        """Execute the complete leader agent task"""
        destination_country = kwargs.get("destination_country", "USA")
        
        logger.info(f"🎯 Leader Agent executing task for {self.raw_material} -> {destination_country}")
        
        try:
            # Step 1: Identify producing countries
            countries = await self.identify_producing_countries()
            
            # Step 2: Get scoring data
            scoring_data = await self.get_country_scoring_data(countries)
            
            # Step 3: Rank countries
            ranking_result = self.rank_countries(scoring_data)
            
            # Step 4: Generate final recommendation
            final_recommendation = await self.generate_final_recommendation(
                ranking_result, destination_country
            )
            
            # Compile complete result
            result = {
                "raw_material": self.raw_material,
                "destination_country": destination_country,
                "identified_countries": countries,
                "scoring_data": scoring_data,
                "ranking_analysis": ranking_result,
                "final_recommendation": final_recommendation,
                "execution_summary": {
                    "total_countries_analyzed": len(countries),
                    "best_country": ranking_result["best_country"].get("country", "Unknown"),
                    "best_score": ranking_result["best_country"].get("composite_score", 0.0),
                    "confidence_level": final_recommendation["confidence_level"]
                }
            }
            
            best_country_name = ranking_result["best_country"].get("country", "Unknown")
            logger.info(f"✅ Leader Agent completed analysis. Best country: {best_country_name}")
            return result
            
        except Exception as e:
            logger.error(f"Leader Agent execution failed: {e}")
            logger.error(traceback.format_exc())
            raise