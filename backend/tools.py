from crewai_tools import tool
import mysql.connector
import requests
import os

@tool("internet_search_tool")
def search_duckduckgo(query: str) -> str:
    """Use DuckDuckGo to search the internet for up-to-date information."""
    res = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
    if res.status_code == 200:
        data = res.json()
        return data.get("Abstract", "No relevant information found.")
    return "Search failed."

@tool("claude_llm_tool")
def query_claude(prompt: str) -> str:
    """Use Anthropic Claude 3.5 LLM to reason about business questions."""
    api_key = os.getenv("CLAUDE_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.json()['content'][0]['text']

@tool("mysql_writer_tool")
def store_score_to_mysql(material: str, country: str, score_type: str, value: float):
    """Store a score value in MySQL for a given material-country-score_type."""
    conn = mysql.connector.connect(
        host="localhost",
        user="autonexus_user",
        password="strongpassword",
        database="autonexus"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO material_scores (material, country, score_type, score_value) VALUES (%s, %s, %s, %s)",
        (material, country, score_type, value)
    )
    conn.commit()
    conn.close()
    return "Stored successfully."