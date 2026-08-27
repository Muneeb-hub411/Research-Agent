import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def _get_gemini_api_key():
    api_key = os.getenv("Gemini_Api_Key") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API Key is missing from environment variables.")
    return api_key

def get_writer_chain(model_name: str = "gemini-3.6-flash"):
    """LCEL chain for the Writer Agent to synthesize scraped data into an article."""
    api_key = _get_gemini_api_key()

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.3,
        google_api_key=api_key
    )
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert technical writer and researcher. Synthesize the provided web search data "
            "and scraped text into a comprehensive, well-structured, and informative report on the given topic."
        ),
        ("human", "Topic: {topic}\n\nScraped Data:\n{scraped_content}")
    ])
    
    # LCEL pipeline
    return prompt | llm | StrOutputParser()

def get_critic_chain(model_name: str = "gemini-3.6-flash"):
    """LCEL chain for the Critic Agent to evaluate and score the written article."""
    api_key = _get_gemini_api_key()

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        google_api_key=api_key
    )
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a strict technical editor and critic. Evaluate the provided draft article for depth, "
            "clarity, factual accuracy based on the context, and structural formatting. "
            "Provide a score out of 10 and clear, constructive feedback for improvement."
        ),
        ("human", "Topic: {topic}\n\nDraft Article:\n{draft}")
    ])
    
    # LCEL pipeline
    return prompt | llm | StrOutputParser()