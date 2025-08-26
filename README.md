# LangGraph Agent with PostgreSQL Checkpointing

A production-ready LangGraph agent with PostgreSQL persistence, deployed on Vercel.

## Features

- 🤖 **LangGraph Agent**: Intelligent conversational agent
- 🗄️ **PostgreSQL Persistence**: Conversation history stored in database
- 🔄 **Thread Management**: Persistent conversation threads
- 🚀 **Vercel Deployment**: Serverless API endpoints
- 🔒 **Secure**: Environment variables for sensitive data

## API Endpoints

- `GET /api/` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/chat` - Send message to agent
- `GET /api/threads/{thread_id}/messages` - Get thread history

## Usage

### Chat with Agent
```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "thread_id": "user-123"
  }'
```

### Get Thread History
```bash
curl https://your-app.vercel.app/api/threads/user-123/messages
```

## Environment Variables

Set these in your Vercel project:

```
DB_HOST=your-postgres-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
DB_PORT=5432
POSTGRES_URI=postgresql://user:pass@host:port/db?sslmode=require
OPENAI_API_KEY=your-openai-key
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file

# Run locally
uvicorn api.chat:app --reload
```

## Deployment

1. Push to GitHub
2. Connect to Vercel
3. Set environment variables
4. Deploy automatically

## Architecture

- **Agent**: LangGraph with PostgreSQL checkpointing
- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL with conversation persistence
- **Deployment**: Vercel serverless functions
