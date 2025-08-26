from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from my_agent.agent import graph
    from langchain_core.messages import HumanMessage
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = self.handle_chat()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_chat(self):
        """Handle chat requests"""
        try:
            if not AGENT_AVAILABLE:
                return {"error": f"Agent not available: {IMPORT_ERROR}"}
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {"error": "No request body"}
                
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            message = request_data.get('message')
            thread_id = request_data.get('thread_id')
            
            if not message or not thread_id:
                return {"error": "Missing message or thread_id"}
            
            # Configure with thread ID for persistence
            config = {"configurable": {"thread_id": thread_id}}
            
            # Create user message
            user_message = HumanMessage(content=message)
            
            # Invoke the graph
            result = graph.invoke(
                {"messages": [user_message]}, 
                config=config
            )
            
            # Extract the assistant's response
            messages = result.get("messages", [])
            if not messages:
                return {"error": "No response from agent"}
            
            # Get the last message (agent's response)
            last_message = messages[-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return {
                "response": response_content,
                "thread_id": thread_id,
                "message_count": len(messages)
            }
            
        except Exception as e:
            return {"error": f"Error processing request: {str(e)}"}