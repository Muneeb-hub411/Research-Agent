import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv()

def get_tavily_search_tool():
    """Initializes and returns the Tavily search tool."""
    api_key = os.getenv("Tavily_Api_Key")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing from environment variables.")
        
    tavily_tool = TavilySearchResults(
        max_results=3,
        tavily_api_key=api_key
    )
    tavily_tool.name = "web_search"
    tavily_tool.description = "Search the web for real-time information, facts, and articles."
    return tavily_tool

def scrape_urls(urls: list[str]) -> str:
    """Scrapes text content from a list of URLs using BeautifulSoup."""
    combined_content = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove unwanted tags
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                    
                text = soup.get_text(separator=" ", strip=True)
                combined_content += f"\n\n--- Source: {url} ---\n{text[:3500]}"
        except Exception as e:
            combined_content += f"\n\n--- Source: {url} (Failed to scrape: {e}) ---"
            
    return combined_content