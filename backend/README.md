# Raw Material Sourcing Workflow

A comprehensive MCP-agent workflow for analyzing raw material sourcing options using multi-agent collaboration.

## Overview

This workflow uses three types of specialized agents to analyze the best countries for sourcing raw materials:

1. **Leader Agent** - Identifies top producing countries and coordinates analysis
2. **Country Agent** - Analyzes specific countries for sourcing potential  
3. **Expert Agent** - Provides specialized analysis on eco-friendliness, profitability, and stability

## Architecture

### Agents
- `LeaderAgent`: Expert of raw material, identifies countries and delegates tasks
- `CountryAgent`: Expert of specific countries, analyzes local conditions
- `ExpertAgent`: Specialized experts in eco-friendliness, profitability, or stability

### Tools
- `DuckDuckGoTool`: Internet search and research
- `ClaudeTool`: LLM analysis and insights
- `MySQLTool`: Database storage and retrieval

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt