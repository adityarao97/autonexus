"""Configuration settings for the workflow"""

# API Keys and Authentication
CLAUDE_API_KEY = ""  # Replace with actual key
DUCKDUCKGO_API_KEY = None  # DuckDuckGo doesn't require API key for basic usage

# Database Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "dummy_user",  # Replace with actual credentials
    "password": "dummy_password",  # Replace with actual credentials
    "database": "sourcing_db",
    "port": 3306
}

# Agent Configuration
AGENT_CONFIG = {
    "max_retries": 3,
    "timeout_seconds": 3000,
    "enable_memory": True
}

# Workflow Configuration
WORKFLOW_CONFIG = {
    "max_countries": 2, #kept as 2 for now to limit the time and resource spent on analysis
    "expert_fields": ["eco-friendly", "profitability", "stability"],
    "scoring_weights": {
        "cost_score": 0.4,
        "stability_score": 0.3,
        "eco_friendly_score": 0.3
    }
}