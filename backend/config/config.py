"""Configuration settings for the workflow"""

# API Keys and Authentication
CLAUDE_API_KEY = "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"  # Replace with actual key
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
    "timeout_seconds": 30,
    "enable_memory": True
}

# Workflow Configuration
WORKFLOW_CONFIG = {
    "max_countries": 3,
    "expert_fields": ["eco-friendly", "profitability", "stability"],
    "scoring_weights": {
        "cost_score": 0.4,
        "stability_score": 0.3,
        "eco_friendly_score": 0.3
    }
}