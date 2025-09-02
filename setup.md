# Company Research Agent Setup

This guide will help you set up the Company Research Agent that combines PostgreSQL database access with real-time data from Perplexity AI.

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+ and Poetry
- PostgreSQL database
- OpenAI API key
- Perplexity AI API key

## Database Setup

1. **Create PostgreSQL Database**
   ```bash
   createdb companies_db
   ```

2. **Run Database Schema**
   ```bash
   psql -d companies_db -f database/schema.sql
   ```

3. **Verify Database Setup**
   ```bash
   psql -d companies_db -c "SELECT COUNT(*) FROM companies;"
   ```

## Environment Configuration

1. **Copy Environment File**
   ```bash
   cp .env.example .env
   ```

2. **Update Environment Variables**
   Edit `.env` file with your actual values:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PERPLEXITY_API_KEY`: Your Perplexity AI API key
   - `DATABASE_URL`: Your PostgreSQL connection string
   - Other configuration as needed

## Installation

1. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

2. **Install Python Dependencies**
   ```bash
   cd agent
   poetry install
   ```

## Running the Application

1. **Start the MCP Server (Terminal 1)**
   ```bash
   cd mcp_server
   python database_server.py
   ```

2. **Start the Python Agent (Terminal 2)**
   ```bash
   cd agent
   poetry run demo
   ```

3. **Start the Frontend (Terminal 3)**
   ```bash
   npm run dev
   ```

4. **Access the Application**
   Open [http://localhost:3000/copilotkit](http://localhost:3000/copilotkit)

## Testing the Agent

Try these example queries with the agent:

### Database Queries
- "Show me information about Apple"
- "Find companies in the technology sector"
- "What companies have a market cap over $1 trillion?"

### Real-time Data Queries
- "What's the latest news about Tesla?"
- "Get recent financial information for Microsoft"
- "What are the current market trends for Amazon?"

### Comparison Queries
- "Compare Apple and Microsoft"
- "How does Tesla compare to traditional automotive companies?"

## Features

### Database Integration
- **Company Search**: Search by name or ticker symbol
- **Industry Filtering**: Filter by industry, sector, market cap
- **Company Details**: Full company profiles with financials

### Real-time Data
- **Latest News**: Recent company news and developments
- **Financial Updates**: Current financial performance and metrics
- **Market Analysis**: Business strategy and competitive analysis

### Frontend Features
- **Interactive UI**: Real-time updates as you chat with the agent
- **Company Cards**: Rich display of company information
- **Theme Customization**: Adjustable color themes
- **Responsive Design**: Works on desktop and mobile

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in .env file
- Ensure database exists and schema is loaded

### API Key Issues
- Verify OPENAI_API_KEY is set correctly
- Check PERPLEXITY_API_KEY is valid
- Ensure API keys have sufficient credits

### MCP Server Issues
- Check if MCP server is running on correct port
- Verify database connection from MCP server
- Check MCP server logs for errors

### Agent Issues
- Verify all Python dependencies are installed
- Check that CopilotKit configuration is correct
- Ensure LangGraph deployment URL is accessible

## Architecture

The system consists of:

1. **Next.js Frontend**: React-based UI with CopilotKit integration
2. **Python Agent**: LangGraph-based agent with tool calling
3. **MCP Server**: Model Context Protocol server for database access
4. **PostgreSQL Database**: Structured company information
5. **Perplexity AI**: Real-time web search and analysis

## Development

### Adding New Company Data
Add data directly to PostgreSQL:
```sql
INSERT INTO companies (name, ticker_symbol, industry, sector, market_cap, employees, founded_year, headquarters, website, description)
VALUES ('Company Name', 'TICK', 'Industry', 'Sector', 1000000000, 5000, 2000, 'City, State', 'https://example.com', 'Description');
```

### Adding New Tools
1. Add tool function to `agent/sample_agent/agent.py`
2. Add tool to the `tools` list
3. Update frontend actions if needed

### Customizing UI
- Modify `src/app/copilotkit/page.tsx` for UI changes
- Update agent state types for new data structures
- Add new CopilotActions for custom interactions