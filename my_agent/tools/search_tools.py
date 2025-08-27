from langchain.tools import tool
from tavily import TavilyClient
import os

@tool
def tavily_search(query: str) -> str:
    """Search the web for current information using Tavily search API."""
    try:
        # Initialize Tavily client inside the function
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = tavily_client.search(query=query, search_depth="basic", max_results=1)
        if response and 'results' in response and response['results']:
            return response['results'][0]['content']
        else:
            return "No results found."
    except Exception as e:
        return f"Error searching: {str(e)}"

tools = [tavily_search]
