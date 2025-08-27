"""
Vercel API handler - Entry point for all routes
"""
from .main import app
from mangum import Mangum

# Create the Vercel handler
handler = Mangum(app, lifespan="off")

# Export for Vercel
def handler_func(event, context):
    return handler(event, context)
