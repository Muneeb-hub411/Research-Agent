import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.tool import get_tavily_search_tool

load_dotenv()

def create_research_agent(model_name: str = "gemini-3.6-flash"):
    """Initializes and returns the Research Agent using modern create_agent and Gemini."""
    api_key = os.getenv("Gemini_Api_Key") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API Key is missing from environment variables.")

    # 1. Initialize the Gemini model instance
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        google_api_key=api_key
    )

    # 2. Get tools list
    tools = [get_tavily_search_tool()]

    # 3. System prompt
    system_prompt = (
        "You are an expert web research assistant. Your goal is to search the web, "
        "gather relevant sources, and find accurate, up-to-date information on the user's topic."
    )

    # 4. Create the modern agent graph
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    return agent