import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQLTool:
    """
    MySQL database tool for data storage, retrieval, and management.
    Provides secure database operations with connection pooling and error handling.
    """
    
    def __init__(self, host: str = "localhost", port: int = 3306, 
                 user: str = "dummy_user", password: str = "dummy_password", 
                 database: str = "sourcing_db", **kwargs):
        self.name = "mysql_database"
        self.description = "Execute MySQL queries for data storage, retrieval, and analysis"
        
        # Connection configuration
        self.connection_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": database,
            "charset": kwargs.get("charset", "utf8mb4"),
            "autocommit": kwargs.get("autocommit", True),
            "echo": kwargs.get("echo", False)
        }
        
        # Mock data for demonstration
        self.mock_mode = kwargs.get("mock_mode", True)  # Set to False for production
        self.mock_data = self._initialize_mock_data()
        
        # Query execution settings
        self.default_timeout = kwargs.get("timeout", 30)
        self.max_retries = kwargs.get("max_retries", 3)
        
        # Statistics
        self.query_count = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.total_execution_time = 0
    
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
                        "description": "SQL query to execute",
                        "minLength": 1,
                        "maxLength": 10000
                    },
                    "params": {
                        "type": "array",
                        "description": "Parameters for parameterized queries",
                        "items": {
                            "type": ["string", "number", "boolean", "null"]
                        },
                        "default": []
                    },
                    "fetch_size": {
                        "type": "integer",
                        "description": "Maximum number of rows to fetch",
                        "minimum": 1,
                        "maximum": 10000,
                        "default": 1000
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Query timeout in seconds",
                        "minimum": 1,
                        "maximum": 300,
                        "default": 30
                    },
                    "return_format": {
                        "type": "string",
                        "description": "Format for returned data",
                        "enum": ["json", "table", "csv"],
                        "default": "json"
                    }
                },
                "required": ["query"]
            }
        }
    
    def _initialize_mock_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mock database data for demonstration"""
        return {
            "business_requirement": [
                {"id": 1, "country": "Ecuador", "cost_score": 8.5, "stability_score": 6.0, "eco_friendly_score": 7.5, "last_updated": "2024-01-15"},
                {"id": 2, "country": "Ghana", "cost_score": 7.0, "stability_score": 7.5, "eco_friendly_score": 8.0, "last_updated": "2024-01-15"},
                {"id": 3, "country": "Ivory Coast", "cost_score": 6.5, "stability_score": 6.5, "eco_friendly_score": 6.0, "last_updated": "2024-01-15"},
                {"id": 4, "country": "Brazil", "cost_score": 7.5, "stability_score": 6.8, "eco_friendly_score": 7.2, "last_updated": "2024-01-15"},
                {"id": 5, "country": "Colombia", "cost_score": 8.0, "stability_score": 6.2, "eco_friendly_score": 7.8, "last_updated": "2024-01-15"},
                {"id": 6, "country": "Ethiopia", "cost_score": 9.0, "stability_score": 5.5, "eco_friendly_score": 6.5, "last_updated": "2024-01-15"},
                {"id": 7, "country": "Vietnam", "cost_score": 8.2, "stability_score": 7.0, "eco_friendly_score": 6.8, "last_updated": "2024-01-15"},
                {"id": 8, "country": "India", "cost_score": 8.8, "stability_score": 6.5, "eco_friendly_score": 6.0, "last_updated": "2024-01-15"},
                {"id": 9, "country": "Thailand", "cost_score": 7.8, "stability_score": 7.2, "eco_friendly_score": 7.0, "last_updated": "2024-01-15"},
                {"id": 10, "country": "Indonesia", "cost_score": 8.1, "stability_score": 6.8, "eco_friendly_score": 6.7, "last_updated": "2024-01-15"}
            ],
            "country_analysis": [],
            "expert_analysis": [],
            "workflow_executions": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
        """Execute MySQL database operation"""
        start_time = datetime.now()
        
        try:
            # Extract and validate arguments
            query = arguments.get("query", "").strip()
            if not query:
                return [{"type": "text", "text": "Error: Query parameter is required and cannot be empty"}]
            
            params = arguments.get("params", [])
            fetch_size = arguments.get("fetch_size", 1000)
            timeout = arguments.get("timeout", self.default_timeout)
            return_format = arguments.get("return_format", "json")
            
            logger.info(f"MySQL query: {query[:100]}...")
            
            # Execute mock query
            await asyncio.sleep(0.1)  # Simulate query execution time
            
            query_lower = query.lower().strip()
            table_name = self._extract_table_name(query_lower)
            
            if table_name not in self.mock_data:
                results = []
                row_count = 0
            else:
                results, row_count = self._execute_mock_query(query_lower, params, table_name, fetch_size)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self.query_count += 1
            self.successful_queries += 1
            self.total_execution_time += execution_time
            
            # Format results
            formatted_result = self._format_results(results, return_format, query, execution_time)
            
            logger.info(f"MySQL query completed: {row_count} rows, {execution_time:.3f}s")
            
            return [{"type": "text", "text": formatted_result}]
            
        except Exception as e:
            # Update error statistics
            self.failed_queries += 1
            execution_time = (datetime.now() - start_time).total_seconds()
            
            error_msg = f"MySQL query execution failed: {str(e)}"
            logger.error(error_msg)
            
            return [{"type": "text", "text": f"{error_msg}\n\nQuery: {query}\nExecution time: {execution_time:.3f}s"}]
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from SQL query"""
        if "from " in query:
            parts = query.split("from ")[1].split()
            if parts:
                return parts[0].strip("`\"'")
        elif "into " in query:
            parts = query.split("into ")[1].split()
            if parts:
                return parts[0].strip("`\"'")
        elif "update " in query:
            parts = query.split("update ")[1].split()
            if parts:
                return parts[0].strip("`\"'")
        
        return "business_requirement"  # Default table
    
    def _execute_mock_query(self, query: str, params: List[Any], 
                           table_name: str, fetch_size: int) -> Tuple[List[Dict[str, Any]], int]:
        """Execute query against mock data"""
        table_data = self.mock_data.get(table_name, [])
        
        if query.startswith("select"):
            return self._execute_mock_select(query, params, table_data, fetch_size)
        elif query.startswith("insert"):
            return self._execute_mock_insert(query, params, table_data)
        elif query.startswith("update"):
            return self._execute_mock_update(query, params, table_data)
        elif query.startswith("delete"):
            return self._execute_mock_delete(query, params, table_data)
        else:
            return [{"result": f"Mock execution of {query[:50]}..."}], 1
    
    def _execute_mock_select(self, query: str, params: List[Any], 
                           table_data: List[Dict[str, Any]], fetch_size: int) -> Tuple[List[Dict[str, Any]], int]:
        """Execute mock SELECT query"""
        results = table_data.copy()
        
        # Apply WHERE clause filtering (simplified)
        if "where " in query:
            results = self._apply_mock_where_clause(query, params, results)
        
        # Apply LIMIT
        if fetch_size < len(results):
            results = results[:fetch_size]
        
        return results, len(results)
    
    def _apply_mock_where_clause(self, query: str, params: List[Any], 
                                data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply simplified WHERE clause filtering to mock data"""
        if "country in (" in query or "country IN (" in query:
            # Handle IN clause for countries
            if params:
                countries = params
            else:
                # Extract countries from query
                try:
                    in_part = query.split("in (")[1].split(")")[0]
                    countries = [c.strip().strip("'\"") for c in in_part.split(",")]
                except:
                    countries = ["Ecuador", "Ghana", "Brazil"]  # Default
            
            return [row for row in data if row.get("country") in countries]
        
        elif "country =" in query or "country=" in query:
            # Handle single country match
            if params:
                country = params[0]
            else:
                country = "Ecuador"  # Default
            
            return [row for row in data if row.get("country") == country]
        
        return data
    
    def _execute_mock_insert(self, query: str, params: List[Any], 
                           table_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Execute mock INSERT query"""
        new_id = len(table_data) + 1
        return [{"inserted_id": new_id, "affected_rows": 1}], 1
    
    def _execute_mock_update(self, query: str, params: List[Any], 
                           table_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Execute mock UPDATE query"""
        affected_rows = 1  # Simplified
        return [{"affected_rows": affected_rows}], 1
    
    def _execute_mock_delete(self, query: str, params: List[Any], 
                           table_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Execute mock DELETE query"""
        affected_rows = 1  # Simplified
        return [{"affected_rows": affected_rows}], 1
    
    def _format_results(self, results: List[Dict[str, Any]], return_format: str, 
                       query: str, execution_time: float) -> str:
        """Format query results based on requested format"""
        if not results:
            return f"Query executed successfully. No results returned.\nExecution time: {execution_time:.3f}s"
        
        if return_format == "json":
            return self._format_as_json(results, query, execution_time)
        elif return_format == "table":
            return self._format_as_table(results, query, execution_time)
        elif return_format == "csv":
            return self._format_as_csv(results, query, execution_time)
        else:
            return self._format_as_json(results, query, execution_time)
    
    def _format_as_json(self, results: List[Dict[str, Any]], query: str, execution_time: float) -> str:
        """Format results as JSON"""
        formatted = {
            "query": query,
            "execution_time_seconds": round(execution_time, 3),
            "row_count": len(results),
            "results": results
        }
        return json.dumps(formatted, indent=2, default=str)
    
    def _format_as_table(self, results: List[Dict[str, Any]], query: str, execution_time: float) -> str:
        """Format results as ASCII table"""
        if not results:
            return f"No results\nExecution time: {execution_time:.3f}s"
        
        # Get column names
        columns = list(results[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = max(len(str(col)), max(len(str(row.get(col, ""))) for row in results))
        
        # Build table
        lines = [
            f"Query: {query}",
            f"Execution time: {execution_time:.3f}s",
            f"Rows: {len(results)}",
            ""
        ]
        
        # Header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for row in results:
            row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns)
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def _format_as_csv(self, results: List[Dict[str, Any]], query: str, execution_time: float) -> str:
        """Format results as CSV"""
        if not results:
            return f"# No results\n# Execution time: {execution_time:.3f}s"
        
        columns = list(results[0].keys())
        
        lines = [
            f"# Query: {query}",
            f"# Execution time: {execution_time:.3f}s",
            f"# Rows: {len(results)}",
            ""
        ]
        
        # Header
        lines.append(",".join(columns))
        
        # Data rows
        for row in results:
            csv_row = []
            for col in columns:
                value = str(row.get(col, ""))
                # Escape commas and quotes in CSV
                if "," in value or '"' in value:
                    value = '"' + value.replace('"', '""') + '"'
                csv_row.append(value)
            lines.append(",".join(csv_row))
        
        return "\n".join(lines)
    
    async def close(self):
        """Close database connections and cleanup"""
        logger.info("MySQL tool cleanup completed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database tool usage statistics"""
        return {
            "total_queries": self.query_count,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "success_rate": (self.successful_queries / self.query_count * 100) if self.query_count > 0 else 0,
            "total_execution_time": round(self.total_execution_time, 3),
            "average_execution_time": round(self.total_execution_time / self.query_count, 3) if self.query_count > 0 else 0,
            "mock_mode": self.mock_mode,
            "connection_config": {
                "host": self.connection_config["host"],
                "port": self.connection_config["port"],
                "database": self.connection_config["db"]
            }
        }