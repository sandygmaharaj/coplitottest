# Company Research Agent

A CopilotKit-powered Company Research Agent that combines PostgreSQL database access with real-time AI analysis from OpenAI. Built with Next.js 15, React 19, and Python LangGraph, featuring a canvas-like interface with streaming research responses.

## Features

- **Canvas Interface**: Dynamic research canvas that appears when queries are made
- **Streaming Research**: Real-time display of AI analysis, news, and financial data
- **Database Integration**: PostgreSQL search for company information
- **OpenAI Research**: Comprehensive company analysis using GPT-4o
- **shadcn/ui Design**: Clean, modern black and white aesthetic
- **Responsive Layout**: Optimized for desktop and mobile

## Architecture Overview

- **Frontend**: Next.js 15 + React 19 with Tailwind CSS and shadcn/ui components
- **Backend**: Python agent using LangGraph and LangChain for AI reasoning
- **Database**: PostgreSQL with company information (currently using mock data)
- **AI Integration**: OpenAI GPT-4o for LLM reasoning and company research
- **State Management**: CopilotKit's useCoAgent for real-time frontend-backend sync

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher, <3.13)
- **OpenAI API Key** (required for AI research functionality)

## Installation

### 1. Clone and Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Environment Variables

Create a `.env` file in the root directory with the required environment variables:

```env
# Required APIs
OPENAI_API_KEY=your_openai_api_key_here

# Database (optional - currently using mock data)
DATABASE_URL=postgresql://username:password@localhost:5432/companies_db

# LangGraph Configuration
LANGGRAPH_DEPLOYMENT_URL=http://localhost:8000
LANGSMITH_API_KEY=your_langsmith_api_key_optional

# Frontend Configuration
NEXT_PUBLIC_COPILOTKIT_AGENT_NAME=CompanyResearchAgent
NEXT_PUBLIC_COPILOTKIT_AGENT_DESCRIPTION="AI-powered company research and analysis"
NEXT_PUBLIC_COPILOTKIT_RUNTIME_URL="http://localhost:3001/copilotkit"
```

## Running the Project

### Quick Start (Two Terminal Setup)

1. **Terminal 1 - Start Python Agent**:
   ```bash
   cd agent
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python -m uvicorn sample_agent.demo:app --reload --port 8000
   ```

2. **Terminal 2 - Start Frontend**:
   ```bash
   npm run dev
   ```

### Access the Application

- **Main Application**: [http://localhost:3001/copilotkit](http://localhost:3001/copilotkit)
- **Agent API**: [http://localhost:8000](http://localhost:8000)

> **Note**: The frontend typically runs on port 3001 if port 3000 is occupied.

## Usage

1. **Initial View**: Clean welcome screen with "Company Research Canvas" title
2. **Start Research**: Type a company query like "Show me information about Apple"
3. **Canvas Expansion**: Interface dynamically expands to show:
   - Company overview card with key information
   - Real-time AI analysis streaming in
   - Recent news and developments
   - Financial data and market insights
4. **Interactive Results**: Click through different sections and explore research data

## Key Components

### Frontend Actions
- `displayCompanyInfo` - Shows company overview cards
- `updateCompanyList` - Displays multiple company results
- `startResearch` - Initiates research status indicator
- `updateResearchAnalysis` - Streams business analysis
- `updateResearchNews` - Streams news updates
- `updateResearchFinancials` - Streams financial data

### Agent Tools
- `search_companies_db` - Searches database for company information
- `search_company_openai` - Gets AI analysis for companies
- `get_company_news` - Retrieves recent company news
- `get_company_financials` - Fetches financial performance data
- `compare_companies` - Compares multiple companies

## Available Scripts

### Frontend
- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run Next.js linting

### Python Agent
- `cd agent && source .venv/bin/activate && python -m sample_agent.demo` - Run agent demo
- `cd agent && source .venv/bin/activate && python -m uvicorn sample_agent.demo:app --reload --port 8000` - Run agent server

## Development Commands (from CLAUDE.md)

All development commands are documented in the `CLAUDE.md` file for Claude Code integration:

- Database setup: `psql -d companies_db -f database/schema.sql`
- MCP server: `python mcp_server/database_server.py`
- Virtual environment setup: `cd agent && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## Troubleshooting

### Common Issues

1. **Port Conflicts**: If port 3000 is occupied, Next.js will automatically use 3001
2. **Agent Connection**: Ensure the agent is running on port 8000 before starting frontend
3. **OpenAI API**: Verify your OpenAI API key is valid and has sufficient credits
4. **Dependencies**: Run `npm install` and `cd agent && source .venv/bin/activate && pip install -r requirements.txt` if modules are missing

### Logs and Debugging

- **Frontend**: Check browser console for React/CopilotKit logs
- **Agent**: Monitor terminal for Python agent execution logs
- **State Sync**: Use browser dev tools to inspect CopilotKit state changes

## Contributing

1. Follow the existing code style and patterns
2. Update CLAUDE.md for any new features or changes
3. Test both frontend and agent components
4. Ensure proper error handling and user feedback

## License

This project is part of the CopilotKit ecosystem. Please refer to CopilotKit's licensing terms.