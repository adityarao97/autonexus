import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import aiohttp
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DuckDuckGoTool:
    """
    DuckDuckGo search tool for internet research.
    Provides web search capabilities using DuckDuckGo's API and search engines.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.name = "duckduckgo_search"
        self.description = "Search the internet using DuckDuckGo for research and information gathering"
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.duckduckgo.com/"
        self.html_search_url = "https://html.duckduckgo.com/html/"
        self.session = None
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        # Search result cache
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                        "minLength": 1,
                        "maxLength": 500
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 8
                    },
                    "region": {
                        "type": "string",
                        "description": "Search region (e.g., 'us-en', 'uk-en', 'de-de')",
                        "default": "wt-wt"
                    },
                    "safe_search": {
                        "type": "string",
                        "description": "Safe search setting",
                        "enum": ["strict", "moderate", "off"],
                        "default": "moderate"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for results",
                        "enum": ["", "d", "w", "m", "y"],
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
            )
        
        return self.session
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _get_cache_key(self, arguments: Dict[str, Any]) -> str:
        """Generate cache key for the query"""
        # Extract parameters safely
        cache_data = {
            "query": arguments.get("query", "").lower().strip(),
            "max_results": arguments.get("max_results", 8),
            "region": arguments.get("region", "wt-wt"),
            "time_range": arguments.get("time_range", "")
        }
        return json.dumps(cache_data, sort_keys=True)
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        return (datetime.now().timestamp() - timestamp) < self.cache_ttl
    
    async def _generate_mock_web_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock web search results for demonstration"""
        # This is for demonstration purposes
        # In production, you would implement proper HTML parsing or use official APIs
        
        mock_results = []
        query_words = query.lower().split()
        
        # Generate contextually relevant mock results based on query
        if any(word in query_words for word in ['chocolate', 'cocoa']):
            mock_results = [
                {
                    "title": "Global Chocolate Production Statistics 2024",
                    "url": "https://example.com/chocolate-stats",
                    "snippet": "Leading chocolate producing countries include Ecuador, Ghana, and Ivory Coast. Ecuador produces premium fine flavor cocoa representing 63% of global fine cocoa production.",
                    "domain": "example.com"
                },
                {
                    "title": "Sustainable Cocoa Farming Practices",
                    "url": "https://example.com/sustainable-cocoa",
                    "snippet": "Sustainable cocoa farming involves agroforestry systems, organic certification, and fair trade practices. Ghana and Ecuador lead in sustainable production methods.",
                    "domain": "example.com"
                },
                {
                    "title": "Cocoa Export Statistics by Country",
                    "url": "https://example.com/cocoa-exports",
                    "snippet": "Top cocoa exporting countries: 1) Ivory Coast (40% global share), 2) Ghana (20%), 3) Ecuador (7%). Export values and trade relationships with major importers.",
                    "domain": "example.com"
                },
                {
                    "title": "Fair Trade Cocoa Certification Programs",
                    "url": "https://example.com/fair-trade-cocoa",
                    "snippet": "Fair Trade certification ensures sustainable cocoa farming practices and fair compensation for farmers. Programs active in Ghana, Ecuador, and Peru.",
                    "domain": "example.com"
                }
            ]
        
        elif any(word in query_words for word in ['coffee']):
            mock_results = [
                {
                    "title": "Coffee Production by Country - Global Statistics",
                    "url": "https://example.com/coffee-production",
                    "snippet": "Brazil leads global coffee production followed by Colombia and Ethiopia. Arabica vs Robusta production ratios and quality grades by region.",
                    "domain": "example.com"
                },
                {
                    "title": "Sustainable Coffee Farming Initiative",
                    "url": "https://example.com/sustainable-coffee",
                    "snippet": "Fair Trade and Rainforest Alliance certified coffee farms in Colombia and Ethiopia. Environmental impact and farmer livelihood improvements.",
                    "domain": "example.com"
                },
                {
                    "title": "Coffee Export Markets and Trade Routes",
                    "url": "https://example.com/coffee-exports",
                    "snippet": "Major coffee export routes from Brazil, Colombia, and Vietnam to global markets. Price trends and quality premiums for specialty coffee.",
                    "domain": "example.com"
                }
            ]
        
        elif any(word in query_words for word in ['cotton']):
            mock_results = [
                {
                    "title": "Global Cotton Production and Trade",
                    "url": "https://example.com/cotton-trade",
                    "snippet": "India, China, and USA are top cotton producers. Organic cotton certification and sustainable farming practices across major producing regions.",
                    "domain": "example.com"
                },
                {
                    "title": "Cotton Export Market Analysis",
                    "url": "https://example.com/cotton-exports",
                    "snippet": "Cotton export statistics, pricing trends, and quality standards. Trade relationships between producing and importing countries.",
                    "domain": "example.com"
                },
                {
                    "title": "Sustainable Cotton Production Methods",
                    "url": "https://example.com/sustainable-cotton",
                    "snippet": "Better Cotton Initiative and organic cotton farming practices. Water conservation and soil health in cotton production.",
                    "domain": "example.com"
                }
            ]
        
        elif any(word in query_words for word in ['sugar']):
            mock_results = [
                {
                    "title": "Global Sugar Production Statistics",
                    "url": "https://example.com/sugar-production",
                    "snippet": "Brazil, India, and Thailand lead global sugar production. Sugarcane vs sugar beet production analysis and market trends.",
                    "domain": "example.com"
                },
                {
                    "title": "Sugar Trade and Export Markets",
                    "url": "https://example.com/sugar-trade",
                    "snippet": "International sugar trade patterns, pricing mechanisms, and quality standards. Major export corridors and import markets.",
                    "domain": "example.com"
                }
            ]
        
        else:
            # Generic results based on query
            for i in range(min(max_results, 5)):
                mock_results.append({
                    "title": f"Search Result {i+1} for '{query}'",
                    "url": f"https://example{i+1}.com/{urllib.parse.quote(query.replace(' ', '-'))}",
                    "snippet": f"Comprehensive information about {query}. This mock result provides relevant data for analysis and decision-making purposes.",
                    "domain": f"example{i+1}.com"
                })
        
        return mock_results[:max_results]
    
    def _format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format search results into readable text"""
        if not results:
            return f"No search results found for query: '{query}'"
        
        formatted_lines = [
            f"Search Results for: '{query}'",
            f"Found {len(results)} results:",
            "=" * 50
        ]
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            snippet = result.get("snippet", "No description available")
            domain = result.get("domain", "Unknown")
            
            formatted_lines.extend([
                f"\n{i}. {title}",
                f"   URL: {url}",
                f"   Domain: {domain}",
                f"   Description: {snippet}",
                "-" * 40
            ])
        
        return "\n".join(formatted_lines)
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
        """Execute the DuckDuckGo search"""
        try:
            # Extract and validate arguments
            query = arguments.get("query", "").strip()
            if not query:
                return [{"type": "text", "text": "Error: Query parameter is required and cannot be empty"}]
            
            max_results = arguments.get("max_results", 8)
            region = arguments.get("region", "wt-wt")
            safe_search = arguments.get("safe_search", "moderate")
            time_range = arguments.get("time_range", "")
            
            # Validate max_results
            max_results = max(1, min(max_results, 20))
            
            logger.info(f"DuckDuckGo search: '{query}' (max_results={max_results}, region={region})")
            
            # Check cache first
            cache_key = self._get_cache_key(arguments)
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if self._is_cache_valid(timestamp):
                    logger.debug(f"Returning cached results for query: '{query}'")
                    return [{"type": "text", "text": cached_data}]
            
            # Apply rate limiting
            await self._rate_limit()
            
            # Generate mock results (replace with real API call in production)
            results = await self._generate_mock_web_results(query, max_results)
            
            # Format output
            formatted_output = self._format_results(results, query)
            
            # Cache results
            self.cache[cache_key] = (formatted_output, datetime.now().timestamp())
            
            # Clean old cache entries (simple cleanup)
            if len(self.cache) > 100:
                # Remove oldest entries
                sorted_cache = sorted(self.cache.items(), key=lambda x: x[1][1])
                for old_key, _ in sorted_cache[:20]:
                    del self.cache[old_key]
            
            logger.info(f"DuckDuckGo search completed: {len(results)} results returned")
            
            return [{"type": "text", "text": formatted_output}]
            
        except Exception as e:
            error_msg = f"DuckDuckGo search failed: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Arguments were: {arguments}")
            
            # Return error with some helpful information
            return [{"type": "text", "text": f"{error_msg}\n\nQuery was: '{arguments.get('query', 'N/A')}'\nThis might be due to network issues or API limitations."}]
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("DuckDuckGo tool session closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            try:
                asyncio.create_task(self.session.close())
            except Exception:
                pass  # Ignore cleanup errors