import os
from dotenv import load_dotenv
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.tool import get_tavily_search_tool

load_dotenv()

def create_research_agent():
    """Initializes and returns the Research Agent Executor using Gemini and Tavily."""
    api_key = os.getenv("Gemini_Api_Key")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing from environment variables.")

  
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
        google_api_key=api_key
    )

    # 2. Get the Tavily search tool
    tools = [get_tavily_search_tool()]

    # 3. Define the prompt for the research agent
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert web research assistant. Your goal is to search the web, gather relevant sources, "
            "and find accurate, up-to-date information on the user's requested topic using the web_search tool."
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Create the tool-calling agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 5. Wrap it inside the AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor