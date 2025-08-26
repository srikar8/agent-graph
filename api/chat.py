from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from my_agent.agent import graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="LangGraph Agent API", version="1.0.0")

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    message_count: int

@app.get("/")
async def root():
    return {"message": "LangGraph Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "langgraph-agent"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a message to the agent and get a response
    """
    try:
        # Configure with thread ID for persistence
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Create user message
        user_message = HumanMessage(content=request.message)
        
        # Invoke the graph
        result = graph.invoke(
            {"messages": [user_message]}, 
            config=config
        )
        
        # Extract the assistant's response
        messages = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No response from agent")
        
        # Get the last message (agent's response)
        last_message = messages[-1]
        response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return ChatResponse(
            response=response_content,
            thread_id=request.thread_id,
            message_count=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """
    Get all messages from a specific thread
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        state = graph.get_state(config)
        messages = state.values.get("messages", [])
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.type if hasattr(msg, 'type') else "unknown",
                "content": msg.content if hasattr(msg, 'content') else str(msg),
                "timestamp": getattr(msg, 'timestamp', None)
            })
        
        return {
            "thread_id": thread_id,
            "messages": formatted_messages,
            "message_count": len(formatted_messages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

# For Vercel deployment
from mangum import Mangum

handler = Mangum(app)
