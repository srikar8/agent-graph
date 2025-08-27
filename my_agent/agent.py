from typing import TypedDict
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from my_agent.nodes import call_model, should_continue, tool_node
from my_agent.utils.state import AgentState

# Load environment variables
load_dotenv()


class GraphConfig(TypedDict):
    pass


workflow = StateGraph(AgentState, config_schema=GraphConfig)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

workflow.add_edge("action", "agent")

# PostgreSQL checkpointer configuration - using environment variables only
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER") 
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Missing required database environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")

# Enhanced connection string with SSL and connection pooling
DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&application_name=langgraph_agent&connect_timeout=30"

# PostgreSQL checkpointer setup - conditional for environment compatibility
# LangGraph Studio refuses to start with ANY custom checkpointer
# We'll detect the environment and only use checkpointer for local development

import sys

# Detect if running in LangGraph Studio/API environment
is_langgraph_studio = (
    # Check if being imported by LangGraph API components
    any('langgraph_api' in module for module in sys.modules.keys()) or
    any('langgraph_runtime' in module for module in sys.modules.keys()) or
    # Check for LangGraph CLI execution
    'langgraph' in sys.argv[0] if sys.argv else False
)

if is_langgraph_studio:
    # LangGraph Studio: Use built-in persistence (no custom checkpointer)
    # Studio will automatically use POSTGRES_URI environment variable
    graph = workflow.compile()
    print("🏢 Running in LangGraph Studio - using built-in persistence via POSTGRES_URI")
else:
    # Local development: Use official PostgresSaver with manual context management
    from langgraph.checkpoint.postgres import PostgresSaver
    
    print("💻 Running locally - configuring official PostgresSaver")
    
    # Create and manually manage the checkpointer context
    _checkpointer_context = PostgresSaver.from_conn_string(DB_URI)
    
    try:
        # Enter the context manager manually to get the actual checkpointer
        checkpointer = _checkpointer_context.__enter__()
        
        # Setup database schema (creates tables if they don't exist)
        checkpointer.setup()
        
        # Compile graph with the official PostgresSaver
        graph = workflow.compile(checkpointer=checkpointer)
        print("✅ Official PostgresSaver configured successfully with manual context management")
        
    except Exception as e:
        print(f"⚠️  PostgresSaver setup failed: {e}")
        # Cleanup on error
        try:
            _checkpointer_context.__exit__(None, None, None)
        except:
            pass
        # Fallback: compile without checkpointer
        graph = workflow.compile()
        print("⚠️  Running without checkpointer as fallback")
