import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import traceback

# Direct imports instead of MCP
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.claude_tool import ClaudeTool
from tools.mysql_tool import MySQLTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the raw material sourcing workflow.
    Provides common functionality for tool usage, memory management, and communication.
    """
    
    def __init__(self, role: str, goal: str, agent_id: Optional[str] = None):
        self.role = role
        self.goal = goal
        self.agent_id = agent_id or f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize tools
        self.tools = {
            "duckduckgo": DuckDuckGoTool(),
            "claude": ClaudeTool(),
            "mysql": MySQLTool()
        }
        
        # Agent memory and state
        self.memory = {}
        self.execution_history = []
        self.status = "initialized"
        self.error_count = 0
        self.max_retries = 3
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        self.execution_time = None
        
        logger.info(f"Initialized {self.__class__.__name__} with role: {role}")
    
    def _extract_text_from_result(self, result: Any) -> str:
        """Extract text content from tool result"""
        try:
            # Handle different result formats
            if isinstance(result, str):
                return result
            
            elif isinstance(result, list):
                if len(result) == 0:
                    return "No result returned"
                
                first_item = result[0]
                
                # Handle list of dictionaries with 'text' key
                if isinstance(first_item, dict):
                    if "text" in first_item:
                        return first_item["text"]
                    elif "content" in first_item:
                        return first_item["content"]
                    else:
                        # Return the string representation of the dict
                        return json.dumps(first_item, indent=2)
                
                # Handle list of strings
                elif isinstance(first_item, str):
                    return first_item
                
                # Handle other types in list
                else:
                    return str(first_item)
            
            elif isinstance(result, dict):
                # Handle dictionary results
                if "text" in result:
                    return result["text"]
                elif "content" in result:
                    return result["content"]
                elif "message" in result:
                    return result["message"]
                elif "result" in result:
                    return str(result["result"])
                else:
                    # Return JSON representation
                    return json.dumps(result, indent=2)
            
            else:
                # Handle any other type
                return str(result)
                
        except Exception as e:
            logger.error(f"Error extracting text from result: {e}")
            return f"Error processing result: {str(e)}"
    
    async def use_tool(self, tool_name: str, arguments: Dict[str, Any], retry_count: int = 0) -> str:
        """
        Use a specific tool with error handling and retry logic
        """
        if tool_name not in self.tools:
            error_msg = f"Tool {tool_name} not available. Available tools: {list(self.tools.keys())}"
            logger.error(error_msg)
            return error_msg
        
        try:
            logger.info(f"Agent {self.agent_id} using tool {tool_name}")
            logger.debug(f"Tool arguments: {arguments}")
            
            # Execute tool
            result = await self.tools[tool_name].execute(arguments)
            
            # Extract text content from result
            text_result = self._extract_text_from_result(result)
            
            # Log successful execution
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "arguments": arguments,
                "status": "success",
                "result_length": len(text_result)
            })
            
            logger.debug(f"Tool {tool_name} result length: {len(text_result)} characters")
            return text_result
            
        except Exception as e:
            error_msg = f"Error using tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Tool arguments were: {arguments}")
            logger.error(traceback.format_exc())
            
            # Log failed execution
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "arguments": arguments,
                "status": "error",
                "error": str(e)
            })
            
            # Retry logic
            if retry_count < self.max_retries:
                logger.info(f"Retrying tool {tool_name} (attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.use_tool(tool_name, arguments, retry_count + 1)
            
            self.error_count += 1
            return f"Failed to execute {tool_name} after {self.max_retries} attempts: {error_msg}"
    
    def store_memory(self, key: str, value: Any, category: str = "general") -> None:
        """Store information in agent memory with categorization"""
        if category not in self.memory:
            self.memory[category] = {}
        
        self.memory[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": type(value).__name__
        }
        
        logger.debug(f"Agent {self.agent_id} stored memory: {category}.{key}")
    
    def get_memory(self, key: str, category: str = "general") -> Any:
        """Retrieve information from agent memory"""
        if category in self.memory and key in self.memory[category]:
            return self.memory[category][key]["value"]
        return None
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of all stored memory"""
        summary = {}
        for category, items in self.memory.items():
            summary[category] = {
                "item_count": len(items),
                "keys": list(items.keys()),
                "last_updated": max([item["timestamp"] for item in items.values()]) if items else None
            }
        return summary
    
    def clear_memory(self, category: Optional[str] = None) -> None:
        """Clear agent memory"""
        if category:
            self.memory.pop(category, None)
            logger.info(f"Agent {self.agent_id} cleared memory category: {category}")
        else:
            self.memory.clear()
            logger.info(f"Agent {self.agent_id} cleared all memory")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and performance metrics"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "error_count": self.error_count,
            "execution_time": self.execution_time,
            "memory_categories": list(self.memory.keys()),
            "total_tool_executions": len(self.execution_history),
            "successful_executions": len([h for h in self.execution_history if h["status"] == "success"]),
            "failed_executions": len([h for h in self.execution_history if h["status"] == "error"])
        }
    
    async def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters for the agent"""
        # Base validation - can be overridden by subclasses
        return True
    
    async def pre_execute(self, **kwargs) -> None:
        """Pre-execution setup and validation"""
        self.start_time = datetime.now()
        self.status = "executing"
        
        # Validate inputs
        if not await self.validate_inputs(**kwargs):
            raise ValueError("Input validation failed")
        
        logger.info(f"Agent {self.agent_id} starting execution")
    
    async def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-execution cleanup and result processing"""
        self.end_time = datetime.now()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.status = "completed" if self.error_count == 0 else "completed_with_errors"
        
        # Add execution metadata to result
        result["execution_metadata"] = {
            "agent_id": self.agent_id,
            "execution_time": self.execution_time,
            "error_count": self.error_count,
            "status": self.status,
            "timestamp": self.end_time.isoformat()
        }
        
        logger.info(f"Agent {self.agent_id} completed execution in {self.execution_time:.2f} seconds")
        return result
    
    @abstractmethod
    async def execute_task(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's specific task - must be implemented by subclasses"""
        pass
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Main execution method with error handling and lifecycle management"""
        try:
            await self.pre_execute(**kwargs)
            result = await self.execute_task(**kwargs)
            return await self.post_execute(result)
            
        except Exception as e:
            self.status = "failed"
            self.error_count += 1
            error_msg = f"Agent {self.agent_id} execution failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return {
                "status": "failed",
                "error": error_msg,
                "agent_id": self.agent_id,
                "execution_metadata": {
                    "error_count": self.error_count,
                    "status": self.status,
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, role={self.role})"
    
    def __repr__(self) -> str:
        return self.__str__()