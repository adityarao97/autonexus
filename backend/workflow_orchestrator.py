import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import traceback

# Import agents
from agents.leader_agent import LeaderAgent
from agents.country_agent import CountryAgent
from agents.expert_agent import ExpertAgent

# Import tools for direct database access
from tools.mysql_tool import MySQLTool

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WorkflowExecutionError(Exception):
    """Custom exception for workflow execution errors"""
    pass

class AgentCoordinationError(Exception):
    """Custom exception for agent coordination errors"""
    pass

class RawMaterialSourcingWorkflow:
    """
    Enhanced workflow orchestrator for comprehensive raw material sourcing analysis.
    
    This workflow:
    1. Identifies key raw materials (max 3) using pure LLM analysis
    2. For each material, finds top countries (max 3) 
    3. For each country, gets expert analysis on profitability, stability, eco-friendliness
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the workflow orchestrator"""
        # Store config first to access priority
        self.config = config or {}
        
        # Get priority from config
        self.priority = self.config.get("priority", "balanced")
        
        # Now get default config which will use the priority
        self.config = {**self._get_default_config(), **self.config}
        
        # Update scoring weights based on priority
        self.scoring_weights = self.config["scoring_weights"]
        self.execution_id = str(uuid.uuid4())
        self.workflow_start_time = None
        self.workflow_end_time = None
        
        # Workflow state
        self.current_phase = "INITIALIZATION"
        self.status = "PENDING"
        self.results = {}
        self.agents = {}
        self.errors = []
        self.warnings = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_api_calls": 0,
            "total_tokens_used": 0,
            "database_queries": 0,
            "search_queries": 0,
            "agent_executions": 0,
            "successful_agents": 0,
            "failed_agents": 0
        }
        
        # Database connection
        self.db_tool = MySQLTool(
            host=self.config.get("database", {}).get("host", "localhost"),
            user=self.config.get("database", {}).get("user", "sourcing_app"),
            password=self.config.get("database", {}).get("password", "secure_password"),
            database=self.config.get("database", {}).get("database", "sourcing_db"),
            mock_mode=self.config.get("database", {}).get("mock_mode", True)
        )
        
        # Agent coordination settings
        self.max_concurrent_agents = self.config.get("concurrency", {}).get("max_agents", 5)
        self.agent_timeout = self.config.get("timeouts", {}).get("agent_timeout", 300)
        self.workflow_timeout = self.config.get("timeouts", {}).get("workflow_timeout", 1800)
        
        logger.info(f"🚀 Enhanced workflow orchestrator initialized with execution ID: {self.execution_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the workflow"""
        priority = self.config.get("priority", "balanced") if hasattr(self, 'config') else "balanced"
    
    # Dynamic scoring weights based on priority
        if priority == "profitability":
            scoring_weights = {
                "profitability": 0.6,
                "stability": 0.2,
                "eco_friendly": 0.2
            }
        elif priority == "stability":
            scoring_weights = {
                "profitability": 0.2,
                "stability": 0.6,
                "eco_friendly": 0.2
            }
        elif priority == "eco-friendly":
            scoring_weights = {
                "profitability": 0.2,
                "stability": 0.2,
                "eco_friendly": 0.6
            }
        else:  # balanced
            scoring_weights = {
                "profitability": 0.4,
                "stability": 0.3,
                "eco_friendly": 0.3
            }
        return {
            "max_raw_materials": 3,
            "max_countries_per_material": 3,
            "expert_fields": ["profitability", "stability", "eco-friendly"],
            "scoring_weights": scoring_weights,
            "analysis_depth": "COMPREHENSIVE",
            "concurrency": {
                "max_agents": 5,
                "max_country_agents": 3,
                "max_expert_agents": 3
            },
            "timeouts": {
                "agent_timeout": 300,
                "workflow_timeout": 2400,  # 40 minutes for comprehensive analysis
                "database_timeout": 30
            },
            "database": {
                "host": "localhost",
                "user": "sourcing_app", 
                "password": "secure_password",
                "database": "sourcing_db",
                "mock_mode": True
            },
            "quality_controls": {
                "min_confidence_level": 6.0,
                "require_expert_consensus": True,
                "validate_data_sources": True
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 5,
                "fail_fast": False,
                "continue_on_agent_failure": True
            }
        }
    
    async def _identify_raw_materials(self, industry_context: str, destination_country: str) -> List[str]:
        """Identify key raw materials using LLM with STRICT output constraints"""
        logger.info(f"🔍 Using LLM to identify raw materials for: {industry_context}")

        # Create a Claude tool instance for this specific task
        from tools.claude_tool import ClaudeTool
        claude_tool = ClaudeTool()

        claude_prompt = (
        f'For the industry "{industry_context}", return ONLY a valid JSON object listing exactly 3 raw materials used as inputs, '
        f'with NO explanation, NO markdown, NO extra text. '
        f'Format: {{"raw_materials": ["Material 1", "Material 2", "Material 3"]}}'
)

        try:
            logger.info("🤖 Making LLM call with strict constraints...")
            logger.info(f"Prompt sent to Claude:\n{claude_prompt}")

            # Make the LLM call with very specific instructions
            response = await claude_tool.execute({
                "prompt": claude_prompt,
                "max_tokens": 200,  # Severely limit tokens to force concise response
                "temperature": 0.0,  # Zero temperature for maximum consistency
                "response_format": "json"
            })

            # Extract text from response
            response_text = self._extract_text_from_result(response)
            logger.info(f"📄 Raw LLM response: {response_text!r}")  # Print with repr to show whitespace/formatting

            # Clean and parse the response
            materials = self._parse_simple_json_response(response_text, industry_context)

            if not materials:
                logger.error("❌ LLM failed to return valid materials")
                logger.error(f"Expected format: {{'raw_materials': ['Material 1', 'Material 2', 'Material 3']}}")
                logger.error(f"Actual response: {response_text!r}")
                raise WorkflowExecutionError(f"LLM could not identify raw materials for '{industry_context}'. Please try with a more specific industry description.")

            # Validate we have exactly 3 materials
            if len(materials) != 3:
                logger.warning(f"Expected 3 materials, got {len(materials)}. Adjusting...")
                if len(materials) > 3:
                    materials = materials[:3]
                elif len(materials) < 3:
                    # Add fallback materials if needed
                    materials.extend(self._get_emergency_materials(industry_context, 3 - len(materials)))

            logger.info(f"✅ LLM identified materials: {materials}")
            return materials

        except Exception as e:
            logger.error(f"❌ LLM-based material identification failed: {e}")
            error_msg = f"Failed to identify raw materials for '{industry_context}'. LLM analysis error: {str(e)}"
            raise WorkflowExecutionError(error_msg)

    def _parse_simple_json_response(self, response_text: str, industry_context: str) -> List[str]:
        """Parse LLM response with simple, strict JSON parsing"""
        try:
            # Clean the response
            response_text = response_text.strip()
            
            # Remove any markdown formatting
            import re
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            logger.debug(f"Cleaned response: {response_text}")
            
            # Find JSON object
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                logger.error("No JSON braces found in response")
                return []
            
            json_text = response_text[start_idx:end_idx+1]
            logger.debug(f"Extracted JSON: {json_text}")
            
            # Parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                logger.error(f"Attempted to parse: {json_text}")
                return []
            
            # Extract materials
            if isinstance(data, dict) and "raw_materials" in data:
                raw_materials = data["raw_materials"]
                if isinstance(raw_materials, list):
                    materials = []
                    for item in raw_materials:
                        if isinstance(item, str) and item.strip():
                            materials.append(item.strip())
                    
                    logger.info(f"Successfully extracted {len(materials)} materials from JSON")
                    for i, material in enumerate(materials, 1):
                        logger.info(f"  {i}. {material}")
                    
                    return materials
            
            logger.error(f"Invalid JSON structure: {data}")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            return []

    def _get_emergency_materials(self, industry_context: str, needed_count: int) -> List[str]:
        """Get emergency fallback materials if LLM doesn't return enough"""
        context_lower = industry_context.lower()
        
        emergency_materials = {
            'tissue': ['Wood Pulp', 'Recycled Paper', 'Bleaching Chemicals'],
            'paper': ['Wood Pulp', 'Recycled Paper', 'Water'],
            'cotton': ['Cotton Fiber', 'Polyester', 'Textile Dyes'],
            'textile': ['Cotton Fiber', 'Polyester', 'Chemical Dyes'],
            'chocolate': ['Cocoa Beans', 'Sugar', 'Milk Powder'],
            'smartphone': ['Lithium', 'Rare Earth Elements', 'Copper'],
            'automotive': ['Steel', 'Aluminum', 'Rubber'],
            'electronics': ['Copper', 'Lithium', 'Silicon'],
            'furniture': ['Timber', 'Steel', 'Fabric'],
            'cosmetics': ['Essential Oils', 'Titanium Dioxide', 'Palm Oil'],
            'food': ['Sugar', 'Wheat', 'Soybeans'],
            'beverage': ['Sugar', 'Water', 'Flavorings']
        }
        
        # Find best match
        for key, materials in emergency_materials.items():
            if key in context_lower:
                return materials[:needed_count]
        
        # Generic fallback
        generic_materials = ['Steel', 'Aluminum', 'Plastic']
        return generic_materials[:needed_count]

    def _extract_text_from_result(self, result: Any) -> str:
        """Extract text content from tool result"""
        try:
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "text" in result[0]:
                    return result[0]["text"]
            elif isinstance(result, dict) and "text" in result:
                return result["text"]
            return str(result)
        except Exception as e:
            logger.error(f"Error extracting text from result: {e}")
            return str(result)

        """Parse LLM response with strict JSON requirements - NO FALLBACKS"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Find JSON content
            import re
            
            # Look for JSON object - more flexible pattern
            json_pattern = r'\{[^{}]*"raw_materials"[^{}]*\[[^\]]*\][^{}]*\}'
            json_matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if not json_matches:
                # Try simpler pattern
                json_pattern = r'\{.*?\}'
                json_matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if not json_matches:
                logger.error("No JSON found in LLM response")
                logger.debug(f"Response was: {response_text}")
                return []
            
            # Try each JSON match
            for json_text in json_matches:
                try:
                    # Clean up the JSON
                    json_text = json_text.strip()
                    
                    # Parse JSON
                    data = json.loads(json_text)
                    logger.debug(f"Parsed JSON: {data}")
                    
                    # Validate structure
                    if not isinstance(data, dict):
                        logger.warning(f"JSON is not a dictionary: {type(data)}")
                        continue
                    
                    if "raw_materials" not in data:
                        logger.warning("No 'raw_materials' key in JSON")
                        continue
                    
                    raw_materials_list = data["raw_materials"]
                    if not isinstance(raw_materials_list, list):
                        logger.warning(f"'raw_materials' is not a list: {type(raw_materials_list)}")
                        continue
                    
                    # Extract material names
                    materials = []
                    for item in raw_materials_list:
                        if isinstance(item, dict) and "name" in item:
                            material_name = item["name"].strip()
                            if material_name:
                                materials.append(material_name)
                                logger.info(f"  📦 Material: {material_name}")
                                if "reasoning" in item:
                                    logger.debug(f"     Reasoning: {item['reasoning']}")
                        elif isinstance(item, str):
                            material_name = item.strip()
                            if material_name:
                                materials.append(material_name)
                                logger.info(f"  📦 Material: {material_name}")
                    
                    if materials:
                        logger.info(f"✅ Successfully extracted {len(materials)} materials from JSON")
                        return materials[:3]  # Ensure max 3
                    else:
                        logger.warning("No valid materials found in raw_materials list")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed for: {json_text[:200]}... Error: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing JSON: {e}")
                    continue
            
            logger.error("All JSON parsing attempts failed")
            return []
            
        except Exception as e:
            logger.error(f"Critical error in JSON parsing: {e}")
            return []

    def _validate_material_relevance(self, materials: List[str], industry_context: str) -> List[str]:
        """Minimal validation - just ensure we have exactly 3 materials"""
        if not materials:
            raise WorkflowExecutionError(f"No valid materials identified for '{industry_context}'")
        
        # Clean up material names
        cleaned_materials = []
        for material in materials:
            if material and isinstance(material, str):
                cleaned_material = material.strip()
                if cleaned_material:
                    cleaned_materials.append(cleaned_material)
        
        if len(cleaned_materials) < 1:
            raise WorkflowExecutionError(f"No valid materials after cleanup for '{industry_context}'")
        
        # Ensure exactly 3 materials
        while len(cleaned_materials) < 3:
            emergency_materials = self._get_emergency_materials(industry_context, 3 - len(cleaned_materials))
            for em in emergency_materials:
                if em not in cleaned_materials:
                    cleaned_materials.append(em)
                    if len(cleaned_materials) >= 3:
                        break
        
        return cleaned_materials[:3]  # Ensure exactly 3
    
    async def _analyze_material_countries(self, raw_material: str, destination_country: str) -> Dict[str, Any]:
        """Analyze top countries for a specific raw material"""
        logger.info(f"🌍 Analyzing countries for {raw_material}")
        
        # Create leader agent for this material
        priority = self.config.get("priority", "balanced")
        leader_agent = LeaderAgent(raw_material, priority)
        self.agents[f"leader_{raw_material}"] = leader_agent
        
        try:
            # Execute leader agent to get top countries
            leader_result = await asyncio.wait_for(
                leader_agent.run(destination_country=destination_country),
                timeout=self.agent_timeout
            )
            
            self.performance_metrics["agent_executions"] += 1
            
            if leader_result.get("status") == "failed":
                self.performance_metrics["failed_agents"] += 1
                logger.error(f"Leader agent failed for {raw_material}")
                return {
                    "status": "failed",
                    "error": leader_result.get("error", "Unknown error"),
                    "countries": self._get_fallback_countries(raw_material)
                }
            
            self.performance_metrics["successful_agents"] += 1
            
            # Extract top countries
            countries = leader_result.get("identified_countries", [])
            if not countries:
                # Fallback countries
                countries = self._get_fallback_countries(raw_material)
            
            # Limit to max countries
            countries = countries[:self.config["max_countries_per_material"]]
            
            logger.info(f"✅ Identified {len(countries)} countries for {raw_material}: {countries}")
            
            return {
                "status": "success",
                "raw_material": raw_material,
                "countries": countries,
                "leader_analysis": leader_result,
                "best_country": self._extract_best_country(leader_result)
            }
            
        except asyncio.TimeoutError:
            self.performance_metrics["failed_agents"] += 1
            logger.error(f"Leader agent timed out for {raw_material}")
            return {
                "status": "timeout",
                "error": "Leader agent execution timed out",
                "countries": self._get_fallback_countries(raw_material)
            }
        except Exception as e:
            self.performance_metrics["failed_agents"] += 1
            logger.error(f"Error analyzing countries for {raw_material}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "countries": self._get_fallback_countries(raw_material)
            }
    
    def _get_fallback_countries(self, raw_material: str) -> List[str]:
        """Get fallback countries for a raw material"""
        material_lower = raw_material.lower()
        
        fallback_map = {
            "cocoa": ["Ecuador", "Ghana", "Ivory Coast"],
            "chocolate": ["Ecuador", "Ghana", "Ivory Coast"],
            "coffee": ["Brazil", "Colombia", "Ethiopia"],
            "cotton": ["India", "China", "USA"],
            "polyester": ["China", "India", "USA"],
            "textile": ["China", "India", "Bangladesh"],
            "dye": ["India", "China", "Germany"],
            "dyes": ["India", "China", "Germany"],
            "fiber": ["India", "China", "USA"],
            "sugar": ["Brazil", "India", "Thailand"],
            "wheat": ["Russia", "USA", "Canada"],
            "rice": ["China", "India", "Indonesia"],
            "milk": ["New Zealand", "Netherlands", "Germany"],
            "vanilla": ["Madagascar", "Indonesia", "Mexico"],
            "steel": ["China", "India", "Japan"],
            "aluminum": ["China", "Russia", "Canada"],
            "copper": ["Chile", "Peru", "China"],
            "lithium": ["Chile", "Australia", "Argentina"],
            "rubber": ["Thailand", "Indonesia", "Malaysia"],
            "wool": ["Australia", "China", "New Zealand"],
            "silk": ["China", "India", "Brazil"],
            "timber": ["Canada", "Russia", "Brazil"],
            "oil": ["Saudi Arabia", "Russia", "USA"],
            "palm": ["Indonesia", "Malaysia", "Thailand"],
            "essential": ["India", "France", "Bulgaria"],
            "titanium": ["Australia", "South Africa", "Canada"]
        }
        
        for key, countries in fallback_map.items():
            if key in material_lower:
                return countries
        
        return ["Brazil", "India", "China"]  # Generic fallback
    
    def _extract_best_country(self, leader_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract best country from leader analysis"""
        try:
            final_rec = leader_result.get("final_recommendation", {})
            if final_rec and "recommended_country" in final_rec:
                return final_rec["recommended_country"]
        except Exception:
            pass
        
        return {"country": "Unknown", "composite_score": 0.0}
    
    async def _analyze_country_experts(self, raw_material: str, country: str, 
                                     destination_country: str) -> Dict[str, Any]:
        """Analyze a country using expert agents"""
        logger.info(f"🔬 Running expert analysis for {country} ({raw_material})")
        
        expert_results = {}
        expert_fields = self.config["expert_fields"]
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config["concurrency"]["max_expert_agents"])
        
        async def run_expert_agent(field: str) -> Tuple[str, Dict[str, Any]]:
            """Run a single expert agent"""
            async with semaphore:
                try:
                    # Create expert agent
                    expert_agent = ExpertAgent(field)
                    agent_key = f"expert_{field}_{country}_{raw_material}"
                    self.agents[agent_key] = expert_agent
                    
                    # Execute expert analysis
                    result = await asyncio.wait_for(
                        expert_agent.run(
                            raw_material=raw_material,
                            country=country,
                            destination_country=destination_country
                        ),
                        timeout=self.agent_timeout
                    )
                    
                    self.performance_metrics["agent_executions"] += 1
                    
                    if result.get("status") == "failed":
                        self.performance_metrics["failed_agents"] += 1
                        logger.error(f"Expert {field} failed for {country}")
                        return field, {
                            "status": "failed",
                            "error": result.get("error", "Unknown error"),
                            "expert_score": 5.0  # Default neutral score
                        }
                    
                    self.performance_metrics["successful_agents"] += 1
                    logger.info(f"✅ Expert {field} completed for {country}")
                    
                    return field, result
                    
                except asyncio.TimeoutError:
                    self.performance_metrics["failed_agents"] += 1
                    logger.error(f"Expert {field} timed out for {country}")
                    return field, {
                        "status": "timeout",
                        "error": "Expert agent execution timed out",
                        "expert_score": 5.0
                    }
                except Exception as e:
                    self.performance_metrics["failed_agents"] += 1
                    logger.error(f"Expert {field} failed for {country}: {e}")
                    return field, {
                        "status": "failed",
                        "error": str(e),
                        "expert_score": 5.0
                    }
        
        # Run all expert agents concurrently
        try:
            tasks = [run_expert_agent(field) for field in expert_fields]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Expert agent task failed: {result}")
                    continue
                
                field, expert_result = result
                expert_results[field] = expert_result
            
            # Calculate overall country score
            country_score = self._calculate_country_score(expert_results)
            
            return {
                "status": "success",
                "country": country,
                "raw_material": raw_material,
                "expert_results": expert_results,
                "overall_score": country_score,
                "expert_scores": self._extract_expert_scores(expert_results)
            }
            
        except Exception as e:
            logger.error(f"Error coordinating expert agents for {country}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "country": country,
                "raw_material": raw_material,
                "expert_results": {},
                "overall_score": 0.0,
                "expert_scores": {}
            }
    
    def _extract_expert_scores(self, expert_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract expert scores from results"""
        scores = {}
        for field, result in expert_results.items():
            if result.get("status") != "failed":
                scores[field] = result.get("expert_score", 5.0)
            else:
                scores[field] = 5.0  # Default for failed analysis
        return scores
    
    def _calculate_country_score(self, expert_results: Dict[str, Any]) -> float:
        """Calculate overall country score from expert results"""
        # Use the priority-based weights
        weights = self.scoring_weights  # Use instance weights instead of config
        total_score = 0.0
        total_weight = 0.0
        
        # Map field names to weight keys
        field_to_weight = {
            "profitability": "profitability",
            "stability": "stability",
            "eco-friendly": "eco_friendly"
        }
        
        for field, result in expert_results.items():
            weight_key = field_to_weight.get(field, field)
            if weight_key in weights:
                score = result.get("expert_score", 5.0)
                weight = weights[weight_key]
                total_score += score * weight
                total_weight += weight
        
        return round(total_score / total_weight if total_weight > 0 else 5.0, 2)
    
    async def execute_comprehensive_workflow(self, industry_context: str = "general sourcing", 
                                           destination_country: str = "USA") -> Dict[str, Any]:
        """Execute the comprehensive raw material sourcing workflow"""
        self.workflow_start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Starting comprehensive workflow for {industry_context} -> {destination_country}")
            
            # Phase 1: Identify Raw Materials
            logger.info("=" * 60)
            logger.info("PHASE 1: IDENTIFYING RAW MATERIALS")
            logger.info("=" * 60)
            
            # FIX: Add await here since _identify_raw_materials is now async
            raw_materials = await self._identify_raw_materials(industry_context, destination_country)
            
            if not raw_materials:
                raise WorkflowExecutionError("No raw materials identified")
            
            self.results["identified_raw_materials"] = raw_materials
            logger.info(f"✅ Phase 1 Complete: {len(raw_materials)} materials identified")
            
            # Phase 2: Analyze Countries for Each Material
            logger.info("\n" + "=" * 60)
            logger.info("PHASE 2: ANALYZING COUNTRIES FOR EACH MATERIAL")
            logger.info("=" * 60)
            
            material_analyses = {}
            
            for material in raw_materials:
                logger.info(f"\n📊 Analyzing {material}...")
                
                # Get countries for this material
                material_result = await self._analyze_material_countries(material, destination_country)
                material_analyses[material] = material_result
                
                if material_result["status"] == "success":
                    countries = material_result["countries"]
                    logger.info(f"✅ {material}: {len(countries)} countries identified - {countries}")
                else:
                    logger.error(f"❌ {material}: Analysis failed - {material_result.get('error', 'Unknown error')}")
            
            self.results["material_analyses"] = material_analyses
            logger.info(f"✅ Phase 2 Complete: Countries analyzed for {len(raw_materials)} materials")
            
            # Phase 3: Expert Analysis for Each Country
            logger.info("\n" + "=" * 60)
            logger.info("PHASE 3: EXPERT ANALYSIS FOR EACH COUNTRY")
            logger.info("=" * 60)
            
            detailed_analysis = {}
            
            for material, material_result in material_analyses.items():
                if material_result["status"] != "success":
                    continue
                
                logger.info(f"\n🔬 Expert analysis for {material}...")
                detailed_analysis[material] = {}
                
                countries = material_result["countries"]
                
                for country in countries:
                    logger.info(f"  Analyzing {country}...")
                    
                    country_expert_result = await self._analyze_country_experts(
                        material, country, destination_country
                    )
                    
                    detailed_analysis[material][country] = country_expert_result
                    
                    if country_expert_result["status"] == "success":
                        scores = country_expert_result["expert_scores"]
                        overall = country_expert_result["overall_score"]
                        logger.info(f"  ✅ {country}: Overall {overall}/10 | " + 
                                  " | ".join([f"{k}: {v:.1f}" for k, v in scores.items()]))
                    else:
                        logger.error(f"  ❌ {country}: Analysis failed")
            
            self.results["detailed_analysis"] = detailed_analysis
            logger.info(f"✅ Phase 3 Complete: Expert analysis completed")
            
            # Phase 4: Generate Final Recommendations
            logger.info("\n" + "=" * 60)
            logger.info("PHASE 4: GENERATING FINAL RECOMMENDATIONS")
            logger.info("=" * 60)
            
            final_recommendations = self._generate_comprehensive_recommendations(
                industry_context, destination_country
            )
            
            self.results["final_recommendations"] = final_recommendations
            
            # Mark workflow as completed
            self.workflow_end_time = datetime.now()
            self.status = "COMPLETED"
            
            execution_time = (self.workflow_end_time - self.workflow_start_time).total_seconds()
            
            logger.info(f"✅ Comprehensive workflow completed in {execution_time:.2f} seconds")
            
            return {
                "execution_id": self.execution_id,
                "status": "COMPLETED",
                "execution_time": execution_time,
                "industry_context": industry_context,
                "destination_country": destination_country,
                "identified_raw_materials": raw_materials,
                "material_analyses": material_analyses,
                "detailed_analysis": detailed_analysis,
                "final_recommendations": final_recommendations,
                "performance_metrics": self.performance_metrics
            }
            
        except Exception as e:
            self.status = "FAILED"
            self.workflow_end_time = datetime.now()
            execution_time = (self.workflow_end_time - self.workflow_start_time).total_seconds()
            
            error_msg = f"Comprehensive workflow failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return {
                "execution_id": self.execution_id,
                "status": "FAILED",
                "error": error_msg,
                "execution_time": execution_time,
                "partial_results": self.results,
                "performance_metrics": self.performance_metrics
            }
    
    def _generate_comprehensive_recommendations(self, industry_context: str, 
                                              destination_country: str) -> Dict[str, Any]:
        """Generate comprehensive recommendations from all analyses"""
        recommendations = {
        "priority_focus": self.config.get("priority", "balanced"),  # NEW
        "scoring_weights_used": self.scoring_weights,  # NEW
        "executive_summary": self._generate_executive_summary(),
        "material_recommendations": {},
        "top_opportunities": [],
        "risk_assessment": {},
        "implementation_roadmap": {}
    }
        
        detailed_analysis = self.results.get("detailed_analysis", {})
        
        # Generate recommendations for each material
        for material, countries_analysis in detailed_analysis.items():
            if not countries_analysis:
                continue
            
            # Find best country for this material
            best_country = None
            best_score = 0.0
            country_rankings = []
            
            for country, analysis in countries_analysis.items():
                if analysis.get("status") == "success":
                    score = analysis.get("overall_score", 0.0)
                    country_rankings.append({
                        "country": country,
                        "overall_score": score,
                        "expert_scores": analysis.get("expert_scores", {}),
                        "status": "analyzed"
                    })
                    
                    if score > best_score:
                        best_score = score
                        best_country = country
            
            # Sort rankings by score
            country_rankings.sort(key=lambda x: x["overall_score"], reverse=True)
            
            recommendations["material_recommendations"][material] = {
                "recommended_country": best_country,
                "recommended_score": best_score,
                "country_rankings": country_rankings,
                "risk_level": self._assess_material_risk(best_score),
                "key_insights": self._generate_material_insights(material, country_rankings)
            }
        
        # Generate top opportunities
        all_opportunities = []
        for material, rec in recommendations["material_recommendations"].items():
            if rec["recommended_country"] and rec["recommended_score"] >= 7.0:
                all_opportunities.append({
                    "material": material,
                    "country": rec["recommended_country"],
                    "score": rec["recommended_score"],
                    "opportunity_rating": "HIGH" if rec["recommended_score"] >= 8.0 else "MEDIUM"
                })
        
        all_opportunities.sort(key=lambda x: x["score"], reverse=True)
        recommendations["top_opportunities"] = all_opportunities[:5]
        
        return recommendations
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary"""
        materials_count = len(self.results.get("identified_raw_materials", []))
        total_countries = sum(len(analysis.get("countries", [])) 
                            for analysis in self.results.get("material_analyses", {}).values())
        
        successful_analyses = sum(1 for material_analysis in self.results.get("detailed_analysis", {}).values()
                                for country_analysis in material_analysis.values()
                                if country_analysis.get("status") == "success")
        
        return f"""
        Comprehensive sourcing analysis completed for {materials_count} strategic raw materials 
        across {total_countries} potential source countries. Expert evaluation conducted on 
        {successful_analyses} country-material combinations across profitability, stability, 
        and eco-friendliness dimensions. Analysis provides actionable recommendations for 
        strategic sourcing decisions with quantified risk assessments.
        """.strip()
    
    def _assess_material_risk(self, score: float) -> str:
        """Assess risk level for a material based on score"""
        if score >= 8.0:
            return "LOW"
        elif score >= 6.5:
            return "MEDIUM"
        elif score >= 5.0:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_material_insights(self, material: str, rankings: List[Dict[str, Any]]) -> List[str]:
        """Generate insights for a specific material"""
        insights = []
        
        if not rankings:
            return ["Insufficient data for analysis"]
        
        top_country = rankings[0]
        top_score = top_country["overall_score"]
        
        # Base insight
        if top_score >= 8.0:
            insights.append(f"Excellent sourcing opportunity with {top_country['country']}")
        elif top_score >= 7.0:
            insights.append(f"Good sourcing potential with {top_country['country']}")
        else:
            insights.append(f"Limited sourcing options - best available: {top_country['country']}")
        
        # Priority-specific insight
        priority = self.config.get("priority", "balanced")
        expert_scores = top_country.get("expert_scores", {})
        
        if expert_scores and priority != "balanced":
            priority_score = expert_scores.get(priority, 0)
            insights.append(f"Priority focus ({priority}): {priority_score:.1f}/10")
        
        # Analyze score patterns
        if expert_scores:
            highest_aspect = max(expert_scores.items(), key=lambda x: x[1])
            lowest_aspect = min(expert_scores.items(), key=lambda x: x[1])
            
            insights.append(f"Strongest in {highest_aspect[0]} ({highest_aspect[1]:.1f}/10)")
            if lowest_aspect[1] < 6.0:
                insights.append(f"Requires attention in {lowest_aspect[0]} ({lowest_aspect[1]:.1f}/10)")
        
        return insights[:4]  # Increased to 4 to include priority insight
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.db_tool.close()
            
            for agent in self.agents.values():
                if hasattr(agent, 'close'):
                    await agent.close()
            
            logger.info(f"Workflow cleanup completed for execution {self.execution_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Convenience functions
async def analyze_industry_sourcing(industry_context: str = "general sourcing", 
                                  destination_country: str = "USA",
                                  config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for comprehensive industry sourcing analysis
    """
    workflow = RawMaterialSourcingWorkflow(config)
    
    try:
        results = await workflow.execute_comprehensive_workflow(industry_context, destination_country)
        return results
    finally:
        await workflow.cleanup()

def print_comprehensive_results(results: Dict[str, Any]):
    """Print comprehensive results in a formatted way"""
    if results["status"] != "COMPLETED":
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE RAW MATERIAL SOURCING ANALYSIS")
    print("="*80)
    
    # Executive Summary
    print(f"Industry Context: {results['industry_context']}")
    print(f"Destination: {results['destination_country']}")
    print(f"Execution Time: {results['execution_time']:.2f} seconds")
    print(f"Analysis Status: {results['status']}")
    
     # NEW: Show priority and weights
    final_recs = results.get("final_recommendations", {})
    priority = final_recs.get("priority_focus", "balanced")
    weights = final_recs.get("scoring_weights_used", {})
    
    print(f"\n🎯 ANALYSIS PRIORITY: {priority.upper()}")
    print(f"Scoring Weights: Profitability={weights.get('profitability', 0):.0%}, "
          f"Stability={weights.get('stability', 0):.0%}, "
          f"Eco-friendly={weights.get('eco_friendly', 0):.0%}")
    
    # Raw Materials Identified
    materials = results.get("identified_raw_materials", [])
    print(f"\n📦 RAW MATERIALS IDENTIFIED ({len(materials)}):")
    for i, material in enumerate(materials, 1):
        print(f"  {i}. {material}")
    
    # Detailed Analysis Results
    detailed_analysis = results.get("detailed_analysis", {})
    
    print(f"\n📊 DETAILED ANALYSIS RESULTS:")
    print("="*60)
    
    for material, countries_analysis in detailed_analysis.items():
        print(f"\n🔸 {material.upper()}")
        print("-" * 40)
        
        if not countries_analysis:
            print("  ❌ No analysis available")
            continue
        
        # Sort countries by score
        country_scores = []
        for country, analysis in countries_analysis.items():
            if analysis.get("status") == "success":
                score = analysis.get("overall_score", 0.0)
                expert_scores = analysis.get("expert_scores", {})
                country_scores.append((country, score, expert_scores))
        
        country_scores.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (country, overall_score, expert_scores) in enumerate(country_scores, 1):
            print(f"\n  {rank}. {country} - Overall Score: {overall_score}/10")
            
            if expert_scores:
                print("     Expert Scores:")
                for field, score in expert_scores.items():
                    print(f"     • {field.title()}: {score:.1f}/10")
    
    # Final Recommendations
    final_recs = results.get("final_recommendations", {})
    
    if "material_recommendations" in final_recs:
        print(f"\n🎯 FINAL RECOMMENDATIONS:")
        print("="*60)
        
        for material, rec in final_recs["material_recommendations"].items():
            best_country = rec.get("recommended_country")
            best_score = rec.get("recommended_score", 0.0)
            risk_level = rec.get("risk_level", "UNKNOWN")
            
            print(f"\n🔸 {material}")
            if best_country:
                print(f"  ✅ Recommended: {best_country} (Score: {best_score}/10)")
                print(f"  📊 Risk Level: {risk_level}")
                
                insights = rec.get("key_insights", [])
                if insights:
                    print("  🔍 Key Insights:")
                    for insight in insights:
                        print(f"     • {insight}")
            else:
                print(f"  ❌ No suitable country identified")
    
    # Top Opportunities
    opportunities = final_recs.get("top_opportunities", [])
    if opportunities:
        print(f"\n🚀 TOP SOURCING OPPORTUNITIES:")
        print("-" * 40)
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp['material']} from {opp['country']} "
                  f"(Score: {opp['score']}/10, {opp['opportunity_rating']} potential)")
    
    # Performance Metrics
    metrics = results.get("performance_metrics", {})
    if metrics:
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"  Total Agent Executions: {metrics.get('agent_executions', 0)}")
        print(f"  Successful Analyses: {metrics.get('successful_agents', 0)}")
        print(f"  Failed Analyses: {metrics.get('failed_agents', 0)}")
        success_rate = (metrics.get('successful_agents', 0) / max(metrics.get('agent_executions', 1), 1)) * 100
        print(f"  Success Rate: {success_rate:.1f}%")

# Main execution function
async def main():
    """Main function for standalone execution"""
    print("🌟 Comprehensive Raw Material Sourcing Analysis")
    print("=" * 60)
    
    # Get user input
    industry_context = input("Enter industry context (e.g., 'cotton t-shirts', 'chocolate manufacturing', 'smartphone assembly'): ").strip()
    if not industry_context:
        industry_context = "cotton t-shirts"  # Default
    
    destination_country = input("Enter destination country (default: USA): ").strip()
    if not destination_country:
        destination_country = "USA"
    
    # NEW: Add priority input
    print("\nSelect your priority for sourcing decisions:")
    print("1. Profitability (focus on cost-effectiveness)")
    print("2. Stability (focus on reliable supply)")
    print("3. Eco-friendly (focus on sustainability)")
    print("4. Balanced (equal weight to all factors)")
    
    priority_choice = input("Enter your choice (1-4, default: 4): ").strip()
    
    priority_map = {
        "1": "profitability",
        "2": "stability", 
        "3": "eco-friendly",
        "4": "balanced"
    }
    
    priority = priority_map.get(priority_choice, "balanced")
    
    print(f"\n🚀 Starting comprehensive analysis...")
    print(f"Industry Context: {industry_context}")
    print(f"Destination: {destination_country}")
    print(f"Priority: {priority.title()}")
    # ... rest of the function
    
    # Pass priority to the workflow
    config = {
        "priority": priority
    }
    
    # Execute comprehensive workflow
    try:
        results = await analyze_industry_sourcing(industry_context, destination_country)
        
        # Display results
        print_comprehensive_results(results)
        
        # Save results to file
        filename = f"comprehensive_sourcing_analysis_{industry_context.replace(' ', '_')}_{destination_country}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n\n⚡ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in main: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())