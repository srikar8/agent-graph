from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum
import os
import sys
from typing import Optional

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from my_agent import graph
    from langchain_core.messages import HumanMessage
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    IMPORT_ERROR = str(e)

app = FastAPI(
    title="LangGraph Agent API",
    description="API for interacting with LangGraph Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    message_count: int

class HealthResponse(BaseModel):
    status: str
    service: str

class APIInfoResponse(BaseModel):
    message: str
    endpoints: dict

class ErrorResponse(BaseModel):
    error: str

@app.get("/", response_model=APIInfoResponse)
async def get_api_info():
    """Get API information and available endpoints"""
    return {
        "message": "LangGraph Agent API is running!",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "langgraph-agent"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests with the LangGraph agent"""
    try:
        if not AGENT_AVAILABLE:
            raise HTTPException(status_code=500, detail=f"Agent not available: {IMPORT_ERROR}")
        
        if not request.message or not request.thread_id:
            raise HTTPException(status_code=400, detail="Missing message or thread_id")
        
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
        
        return {
            "response": response_content,
            "thread_id": request.thread_id,
            "message_count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Vercel serverless handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
