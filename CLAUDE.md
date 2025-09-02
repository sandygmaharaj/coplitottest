# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Next.js Frontend
- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build the application for production
- `npm run start` - Start production server
- `npm run lint` - Run Next.js linting

### Python Agent
- `cd agent && poetry install` - Install Python dependencies
- `cd agent && poetry run demo` - Run the agent demo
- `cd agent && poetry run uvicorn sample_agent.demo:app --reload` - Run agent server

### Database Setup
- `psql -d companies_db -f database/schema.sql` - Initialize PostgreSQL database
- `python mcp_server/database_server.py` - Start MCP server for database access

## Architecture Overview

This is a Company Research Agent built with CopilotKit that combines PostgreSQL database access with real-time data from Perplexity AI:

### Frontend (Next.js 15 + React 19)
- **Framework**: Next.js 15 with App Router, React 19, TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **Main Components**:
  - `src/app/page.tsx` - Root page
  - `src/app/copilotkit/page.tsx` - Company research interface with interactive company cards
  - `src/app/api/copilotkit/route.ts` - API endpoint for CopilotKit runtime

### Python Agent (LangGraph)
- **Framework**: LangGraph with LangChain integration
- **Dependencies**: OpenAI, Anthropic, CopilotKit, asyncpg, aiohttp, MCP
- **Main Files**:
  - `agent/sample_agent/agent.py` - Core agent with company research tools
  - `agent/sample_agent/perplexity_client.py` - Perplexity AI API integration
  - `agent/sample_agent/demo.py` - Agent demo runner
  - `agent/pyproject.toml` - Python dependencies and scripts

### Database Layer
- **Database**: PostgreSQL with companies table
- **Schema**: `database/schema.sql` - Company information schema with sample data
- **MCP Server**: `mcp_server/database_server.py` - Model Context Protocol server for database access

### External APIs
- **Perplexity AI**: Real-time company news, financial data, and analysis
- **OpenAI**: LLM for agent reasoning and response generation

### CopilotKit Integration
- **Runtime**: Uses `@copilotkit/runtime` with LangGraph Platform endpoint
- **Features**:
  - Frontend Actions: Company display, theme changes, company list updates
  - Shared State: Company data synchronization between frontend and backend
  - Generative UI: Dynamic company card rendering
  - Tool integration between React components and Python agent

### State Management
- **Agent State**: Synchronized between frontend and backend via CopilotKit
- **Key State**: 
  - `companies` array - List of company search results
  - `selected_company` - Currently selected company details
  - `search_results` - Raw search results from APIs
- **State Shape**: Defined in both `AgentState` (Python) and `AgentState` type (TypeScript)

### Environment Variables
Required for full functionality:
- `OPENAI_API_KEY` - OpenAI API key for LLM
- `PERPLEXITY_API_KEY` - Perplexity AI API key for real-time data
- `DATABASE_URL` - PostgreSQL connection string
- `LANGGRAPH_DEPLOYMENT_URL` - LangGraph deployment endpoint
- `LANGSMITH_API_KEY` - LangSmith API key for tracing
- `NEXT_PUBLIC_COPILOTKIT_AGENT_NAME` - Agent name for frontend
- `NEXT_PUBLIC_COPILOTKIT_AGENT_DESCRIPTION` - Agent description

## Key Patterns

### Tool Integration
- **Database Tools**: `search_companies_db` for querying PostgreSQL via MCP server
- **Real-time Tools**: `search_company_perplexity`, `get_company_news`, `get_company_financials`, `compare_companies`
- **Frontend Actions**: `displayCompanyInfo`, `updateCompanyList`, `showCompanyCard`
- Agent uses ReAct pattern for tool calling and response generation

### Data Flow
1. User asks about a company
2. Agent searches database for basic company info
3. Agent queries Perplexity AI for real-time data
4. Agent combines results and updates frontend state
5. Frontend renders company information cards

### State Synchronization
- Agent state is shared between frontend and backend using CopilotKit's `useCoAgent` hook
- Company data flows from agent tools to frontend components
- UI updates in real-time as agent processes queries

### Generative UI
- Company card components render dynamically based on agent tool calls
- Interactive company list with click-to-select functionality
- Theme customization for visual appeal

## Development Guidelines

### Adding New Company Data
- Add to PostgreSQL database via `database/schema.sql`
- Ensure MCP server can access new data
- Update database tools if new fields are added

### Adding New Tools
- Define in `agent/sample_agent/agent.py`
- Add to `tools` list for agent binding
- Update frontend actions if UI changes needed

### Customizing UI
- Modify `src/app/copilotkit/page.tsx` for layout changes
- Update `AgentState` type for new data structures
- Add new `useCopilotAction` hooks for custom interactions