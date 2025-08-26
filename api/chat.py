from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from my_agent.agent import graph
from langchain_core.messages import HumanMessage

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if path == '/api/':
            response = {"message": "LangGraph Agent API is running!"}
        elif path == '/api/health':
            response = {"status": "healthy", "service": "langgraph-agent"}
        elif path.startswith('/api/threads/') and path.endswith('/messages'):
            # Extract thread_id from path
            thread_id = path.split('/')[3]
            response = self.get_thread_messages(thread_id)
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/api/chat':
            response = self.handle_chat()
        else:
            response = {"error": "Not found"}
        
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
            # Read request body
            content_length = int(self.headers['Content-Length'])
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
    
    def get_thread_messages(self, thread_id):
        """Get all messages from a specific thread"""
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
            return {"error": f"Error retrieving messages: {str(e)}"}