import asyncio
import json
import logging
from typing import Any, Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeTool:
    """
    Claude LLM tool for advanced AI analysis and insights.
    """
    
    def __init__(self, api_key: str = "dummy_claude_api_key", model: str = "claude-3-sonnet-20240229"):
        self.name = "claude_llm"
        self.description = "Interact with Claude LLM for advanced analysis, reasoning, and insights"
        self.api_key = api_key
        self.model = model
        self.request_count = 0
        self.total_tokens_used = 0
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes cache TTL
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
        """Execute Claude LLM request - MAIN METHOD"""
        try:
            # Validate arguments
            prompt = arguments.get("prompt", "").strip()
            if not prompt:
                return [{"type": "text", "text": "Error: Prompt is required and cannot be empty"}]
            
            max_tokens = arguments.get("max_tokens", 2000)
            temperature = arguments.get("temperature", 0.7)
            model = arguments.get("model", self.model)
            system_prompt = arguments.get("system_prompt", "").strip()
            response_format = arguments.get("response_format", "text")
            
            logger.info(f"Claude request: {len(prompt)} chars, model={model}, temp={temperature}")
            
            # Check cache
            cache_key = self._get_cache_key(arguments)
            if cache_key in self.cache:
                cached_content, timestamp = self.cache[cache_key]
                if (datetime.now().timestamp() - timestamp) < self.cache_ttl:
                    logger.debug("Returning cached Claude response")
                    return [{"type": "text", "text": cached_content}]
            
            # Enhance prompt for desired format
            if response_format == "json":
                enhanced_prompt = f"{prompt}\n\nPlease provide your response in valid JSON format."
            elif response_format == "structured":
                enhanced_prompt = f"{prompt}\n\nPlease provide a well-structured response with clear sections, headings, and bullet points where appropriate."
            else:
                enhanced_prompt = prompt
            
            # Generate mock response (replace with real API call in production)
            await asyncio.sleep(0.5)  # Simulate API processing time
            content = self._generate_contextual_response(enhanced_prompt, system_prompt)
            
            # Update tracking
            self.request_count += 1
            self.total_tokens_used += len(content.split()) * 1.3  # Rough estimate
            
            # Add metadata
            formatted_response = f"{content}\n\n---\nModel: {model}\nTokens (estimated): {len(content.split()) * 1.3:.0f}\nTotal API calls: {self.request_count}"
            
            # Cache response
            self.cache[cache_key] = (formatted_response, datetime.now().timestamp())
            
            # Clean old cache entries
            if len(self.cache) > 50:
                sorted_cache = sorted(self.cache.items(), key=lambda x: x[1][1])
                for old_key, _ in sorted_cache[:10]:
                    del self.cache[old_key]
            
            logger.info(f"Claude response generated: {len(content)} characters")
            
            return [{"type": "text", "text": formatted_response}]
            
        except Exception as e:
            error_msg = f"Claude LLM execution failed: {str(e)}"
            logger.error(error_msg)
            
            return [{"type": "text", "text": f"{error_msg}\n\nThis might be due to API limits, network issues, or invalid parameters. Please check your configuration and try again."}]
    
    def _get_cache_key(self, arguments: Dict[str, Any]) -> str:
        """Generate cache key for the request"""
        cache_data = {
            "prompt": arguments.get("prompt", "").strip(),
            "max_tokens": arguments.get("max_tokens", 2000),
            "temperature": arguments.get("temperature", 0.7),
            "system_prompt": arguments.get("system_prompt", ""),
            "model": arguments.get("model", self.model)
        }
        return json.dumps(cache_data, sort_keys=True)
    
    def _generate_contextual_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate contextual mock response based on prompt content"""
        prompt_lower = prompt.lower()
        # Add this check first:
        if "raw material" in prompt_lower or "raw_materials" in prompt_lower:
            return self._generate_materials_response(prompt)
        
        # Determine response type based on prompt keywords
        if any(word in prompt_lower for word in ["countries", "country", "produce", "production"]):
            return self._generate_country_analysis_response(prompt)
        elif any(word in prompt_lower for word in ["cost", "price", "economic", "profitability"]):
            return self._generate_economic_response(prompt)
        elif any(word in prompt_lower for word in ["environment", "sustainable", "eco", "green"]):
            return self._generate_environmental_response(prompt)
        elif any(word in prompt_lower for word in ["stable", "stability", "risk", "political"]):
            return self._generate_stability_response(prompt)
        elif any(word in prompt_lower for word in ["raw materials", "materials", "input goods"]):
            return self._generate_materials_response(prompt)
        else:
            return self._generate_general_response(prompt)
    
    def _generate_country_analysis_response(self, prompt: str) -> str:
        """Generate country-specific analysis response"""
        # Extract material from prompt
        material = "Unknown"
        for test_material in ["cocoa", "coffee", "sugar", "cotton", "milk", "vanilla"]:
            if test_material in prompt.lower():
                material = test_material.title()
                break
        
        country_mappings = {
            "cocoa": ["Ecuador", "Ghana", "Ivory Coast"],
            "coffee": ["Brazil", "Colombia", "Ethiopia"],
            "sugar": ["Brazil", "India", "Thailand"],
            "cotton": ["India", "China", "USA"],
            "milk": ["New Zealand", "Netherlands", "Germany"],
            "vanilla": ["Madagascar", "Indonesia", "Mexico"]
        }
        
        countries = country_mappings.get(material.lower(), ["Brazil", "India", "China"])
        
        return f"""**Top Producing Countries Analysis for {material}:**

Based on global production data and market analysis, the following countries represent the strongest options:

**1. {countries[0]}**
- Production Capacity: High-volume producer with established infrastructure
- Quality Standards: Premium quality products with international certifications
- Export Experience: Extensive export relationships with major global markets
- Competitive Advantages: Cost-effective production, favorable climate conditions

**2. {countries[1]}**
- Production Capacity: Large-scale operations with modern facilities
- Quality Standards: Consistent quality meeting international requirements
- Export Experience: Strong trade relationships and logistics networks
- Competitive Advantages: Economic stability, reliable supply chains

**3. {countries[2]}**
- Production Capacity: Growing production capabilities with investment in modernization
- Quality Standards: Improving quality standards with certification programs
- Export Experience: Developing export capabilities with government support
- Competitive Advantages: Labor cost advantages, geographic proximity to markets

**Recommendation:**
{countries[0]} emerges as the top choice based on balanced performance across all evaluation criteria.

{{"countries": ["{countries[0]}", "{countries[1]}", "{countries[2]}"]}}"""
    
    def _generate_economic_response(self, prompt: str) -> str:
        """Generate economics-focused response"""
        # Extract country from prompt
        country = "Unknown"
        for test_country in ["Ecuador", "Ghana", "Brazil", "Colombia", "Ethiopia", "India", "China"]:
            if test_country.lower() in prompt.lower():
                country = test_country
                break
        
        # Country-specific economic analysis
        country_economics = {
            "Ecuador": {"score": 8.2, "strengths": "Very competitive cocoa production costs, US dollar economy"},
            "Ghana": {"score": 7.1, "strengths": "Competitive production costs with government support"},
            "Brazil": {"score": 7.8, "strengths": "Large-scale production efficiencies, good infrastructure"},
            "Colombia": {"score": 7.5, "strengths": "Premium quality commands higher prices"},
            "Ethiopia": {"score": 8.9, "strengths": "Lowest production costs globally due to low labor costs"},
            "India": {"score": 8.5, "strengths": "Very competitive labor and production costs"},
            "China": {"score": 7.9, "strengths": "Massive scale and industrial efficiency"}
        }
        
        country_data = country_economics.get(country, {"score": 6.5, "strengths": "Moderate cost structure"})
        
        return f"""**Economic Analysis for {country}:**

**Cost Structure Assessment:**
- {country_data['strengths']}
- Transportation costs vary by infrastructure quality
- Quality premiums available for certified products

**Market Economics:**
- Current market prices show competitive positioning
- Price volatility managed through long-term contracts
- Volume discounts available for large commitments

**Profitability Score: {country_data['score']}/10**

This score reflects the economic competitiveness and profitability potential for sourcing from {country}."""
    
    def _generate_environmental_response(self, prompt: str) -> str:
        """Generate environment-focused response"""
        # Extract country from prompt
        country = "Unknown"
        for test_country in ["Ecuador", "Ghana", "Brazil", "Colombia", "Ethiopia", "India", "China"]:
            if test_country.lower() in prompt.lower():
                country = test_country
                break
        
        eco_scores = {
            "Ecuador": 7.8, "Ghana": 8.1, "Brazil": 6.8, "Colombia": 7.9, 
            "Ethiopia": 6.7, "India": 5.9, "China": 5.2
        }
        
        score = eco_scores.get(country, 7.0)
        
        return f"""**Environmental Sustainability Assessment for {country}:**

**Environmental Impact Analysis:**
- Carbon footprint management through sustainable practices
- Water conservation and recycling programs in place
- Biodiversity protection through agroforestry systems

**Sustainability Certifications:**
- Organic certification programs available
- Fair Trade partnerships with local farmers
- Rainforest Alliance certification adoption

**Environmental Score: {score}/10**

{country} demonstrates {"strong" if score >= 7.5 else "good" if score >= 6.5 else "moderate"} environmental practices with opportunities for improvement."""
    
    def _generate_stability_response(self, prompt: str) -> str:
        """Generate stability-focused response"""
        # Extract country from prompt
        country = "Unknown"
        for test_country in ["Ecuador", "Ghana", "Brazil", "Colombia", "Ethiopia", "India", "China"]:
            if test_country.lower() in prompt.lower():
                country = test_country
                break
        
        stability_scores = {
            "Ecuador": 6.0, "Ghana": 7.8, "Brazil": 6.9, "Colombia": 6.1, 
            "Ethiopia": 5.2, "India": 7.2, "China": 7.5
        }
        
        score = stability_scores.get(country, 6.5)
        
        return f"""**Political and Economic Stability Assessment for {country}:**

**Political Environment:**
- Government stability with {"strong" if score >= 7.5 else "moderate" if score >= 6.0 else "limited"} institutions
- {"Consistent" if score >= 7.0 else "Generally stable" if score >= 6.0 else "Variable"} policy framework
- {"Low" if score >= 7.5 else "Moderate" if score >= 6.0 else "Elevated"} political risk levels

**Economic Indicators:**
- GDP growth trends show {"strong" if score >= 7.5 else "stable" if score >= 6.0 else "variable"} performance
- Currency stability within acceptable ranges
- {"Well-developed" if score >= 7.5 else "Adequate" if score >= 6.0 else "Developing"} financial systems

**Stability Score: {score}/10**

{country} presents a {"low" if score >= 7.5 else "moderate" if score >= 6.0 else "elevated"} risk profile for sourcing operations."""
    
    def _generate_general_response(self, prompt: str) -> str:
        """Generate general response"""
        return f"""Based on comprehensive analysis of the factors mentioned in your query:

**Key Findings:**
- Market analysis shows competitive opportunities with manageable risks
- Multiple strategic options available with varying risk-reward profiles
- Implementation requires careful planning and risk management

**Recommendations:**
- Conduct thorough due diligence before final decisions
- Develop comprehensive risk mitigation strategies
- Establish monitoring and evaluation frameworks
- Maintain flexibility for changing market conditions

This analysis provides a foundation for strategic decision-making based on current market conditions and industry best practices."""
    
    def _generate_materials_response(self, prompt: str) -> str:
        """Generate a strict JSON response for raw materials requests"""
        prompt_lower = prompt.lower()
        # Very basic mapping for demo purposes
        if "chocolate" in prompt_lower:
            return '{"raw_materials": ["Cocoa Beans", "Sugar", "Milk Powder"]}'
        if "cotton" in prompt_lower:
            return '{"raw_materials": ["Cotton Fiber", "Polyester", "Textile Dyes"]}'
        if "tissue" in prompt_lower:
            return '{"raw_materials": ["Wood Pulp", "Recycled Paper", "Bleaching Chemicals"]}'
        if "smartphone" in prompt_lower:
            return '{"raw_materials": ["Lithium", "Rare Earth Elements", "Copper"]}'
        # Default fallback
        return '{"raw_materials": ["Material 1", "Material 2", "Material 3"]}'
    
    async def close(self):
        """Close any resources"""
        logger.info("Claude tool session closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return {
            "total_requests": self.request_count,
            "total_tokens_used": self.total_tokens_used,
            "cache_size": len(self.cache),
            "model": self.model
        }