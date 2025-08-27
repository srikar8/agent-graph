# LangGraph Agent with PostgreSQL Checkpointing

A production-ready LangGraph agent with PostgreSQL persistence, deployed on Vercel.

## Features

- 🤖 **LangGraph Agent**: Intelligent conversational agent
- 🗄️ **PostgreSQL Persistence**: Conversation history stored in database
- 🔄 **Thread Management**: Persistent conversation threads
- 🚀 **Vercel Deployment**: Serverless API endpoints
- 🔒 **Secure**: Environment variables for sensitive data

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check
- `POST /chat` - Send message to agent
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Usage

### Chat with Agent

**Local Development:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "thread_id": "user-123"
  }'
```

**Production (Vercel):**
```bash
curl -X POST https://your-app.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "thread_id": "user-123"
  }'
```

### View Interactive Documentation
- **Local**: `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc)
- **Production**: `https://your-app.vercel.app/docs` (Swagger UI) or `https://your-app.vercel.app/redoc` (ReDoc)

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

# Run the server (option 1 - using the startup script)
python start_server.py

# Run the server (option 2 - using uvicorn directly)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Run the server (option 3 - using the main module)
python -m api.main
```

The server will start on `http://localhost:8000` with:
- Interactive API docs at `http://localhost:8000/docs`
- Alternative docs at `http://localhost:8000/redoc`
- Health check at `http://localhost:8000/health`

## Deployment

### Vercel Deployment

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add FastAPI with Vercel support"
   git push origin main
   ```

3. **Deploy to Vercel**:
   - Visit [vercel.com](https://vercel.com) and connect your GitHub repo
   - Or use CLI: `vercel --prod`

4. **Set Environment Variables** in Vercel dashboard:
   ```
   DB_HOST=your-postgres-host
   DB_USER=your-db-user
   DB_PASSWORD=your-db-password
   DB_NAME=your-db-name
   DB_PORT=5432
   POSTGRES_URI=postgresql://user:pass@host:port/db?sslmode=require
   OPENAI_API_KEY=your-openai-key
   ```

5. **Access your deployed API**:
   - Main API: `https://your-app.vercel.app/`
   - Health check: `https://your-app.vercel.app/health`
   - Chat endpoint: `https://your-app.vercel.app/chat`
   - API docs: `https://your-app.vercel.app/docs`

### Local vs Vercel Differences

- **Local**: Full FastAPI server with uvicorn
- **Vercel**: Serverless functions using Mangum adapter
- **Both**: Same API endpoints and functionality

## Architecture

- **Agent**: LangGraph with PostgreSQL checkpointing
- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL with conversation persistence
- **Deployment**: Vercel serverless functions
