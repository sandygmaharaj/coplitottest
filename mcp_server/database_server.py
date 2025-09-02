"""
MCP Server for PostgreSQL database access to company information.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
import asyncio
import asyncpg
from pydantic import BaseModel, Field

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanySearchParams(BaseModel):
    """Parameters for company search."""
    query: str = Field(description="Company name or ticker symbol to search for")
    limit: int = Field(default=10, description="Maximum number of results to return")

class CompanyFilterParams(BaseModel):
    """Parameters for filtering companies."""
    industry: Optional[str] = Field(default=None, description="Filter by industry")
    sector: Optional[str] = Field(default=None, description="Filter by sector")
    min_market_cap: Optional[int] = Field(default=None, description="Minimum market cap")
    max_market_cap: Optional[int] = Field(default=None, description="Maximum market cap")
    limit: int = Field(default=10, description="Maximum number of results to return")

class DatabaseServer:
    """MCP Server for database operations."""
    
    def __init__(self):
        self.server = Server("database-server")
        self.db_pool: Optional[asyncpg.Pool] = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up the MCP server handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available database resources."""
            return [
                Resource(
                    uri="database://companies",
                    name="Companies Database",
                    description="PostgreSQL database containing company information",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a database resource."""
            if uri == "database://companies":
                return json.dumps({
                    "description": "Companies database with financial and operational data",
                    "tables": ["companies"],
                    "total_records": await self.count_companies()
                })
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available database tools."""
            return [
                Tool(
                    name="search_companies",
                    description="Search for companies by name or ticker symbol",
                    inputSchema=CompanySearchParams.model_json_schema()
                ),
                Tool(
                    name="filter_companies",
                    description="Filter companies by industry, sector, or market cap",
                    inputSchema=CompanyFilterParams.model_json_schema()
                ),
                Tool(
                    name="get_company_details",
                    description="Get detailed information about a specific company",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "integer", "description": "Company ID"},
                            "ticker": {"type": "string", "description": "Company ticker symbol"}
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "search_companies":
                params = CompanySearchParams(**arguments)
                results = await self.search_companies(params.query, params.limit)
                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            
            elif name == "filter_companies":
                params = CompanyFilterParams(**arguments)
                results = await self.filter_companies(
                    industry=params.industry,
                    sector=params.sector,
                    min_market_cap=params.min_market_cap,
                    max_market_cap=params.max_market_cap,
                    limit=params.limit
                )
                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            
            elif name == "get_company_details":
                company_id = arguments.get("company_id")
                ticker = arguments.get("ticker")
                
                if company_id:
                    result = await self.get_company_by_id(company_id)
                elif ticker:
                    result = await self.get_company_by_ticker(ticker)
                else:
                    return [TextContent(type="text", text="Error: Must provide either company_id or ticker")]
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def initialize_database(self):
        """Initialize database connection."""
        database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/companies")
        try:
            self.db_pool = await asyncpg.create_pool(database_url)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def count_companies(self) -> int:
        """Count total number of companies."""
        if not self.db_pool:
            return 0
        
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM companies")
            return result or 0
    
    async def search_companies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search companies by name or ticker symbol."""
        if not self.db_pool:
            return []
        
        async with self.db_pool.acquire() as conn:
            sql = """
                SELECT id, name, ticker_symbol, industry, sector, market_cap, 
                       employees, founded_year, headquarters, website, description
                FROM companies 
                WHERE name ILIKE $1 OR ticker_symbol ILIKE $1
                ORDER BY market_cap DESC NULLS LAST
                LIMIT $2
            """
            rows = await conn.fetch(sql, f"%{query}%", limit)
            return [dict(row) for row in rows]
    
    async def filter_companies(self, industry: Optional[str] = None, sector: Optional[str] = None,
                              min_market_cap: Optional[int] = None, max_market_cap: Optional[int] = None,
                              limit: int = 10) -> List[Dict[str, Any]]:
        """Filter companies by various criteria."""
        if not self.db_pool:
            return []
        
        conditions = []
        params = []
        param_count = 0
        
        if industry:
            param_count += 1
            conditions.append(f"industry ILIKE ${param_count}")
            params.append(f"%{industry}%")
        
        if sector:
            param_count += 1
            conditions.append(f"sector ILIKE ${param_count}")
            params.append(f"%{sector}%")
        
        if min_market_cap:
            param_count += 1
            conditions.append(f"market_cap >= ${param_count}")
            params.append(min_market_cap)
        
        if max_market_cap:
            param_count += 1
            conditions.append(f"market_cap <= ${param_count}")
            params.append(max_market_cap)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        param_count += 1
        params.append(limit)
        
        sql = f"""
            SELECT id, name, ticker_symbol, industry, sector, market_cap, 
                   employees, founded_year, headquarters, website, description
            FROM companies 
            WHERE {where_clause}
            ORDER BY market_cap DESC NULLS LAST
            LIMIT ${param_count}
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [dict(row) for row in rows]
    
    async def get_company_by_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get company details by ID."""
        if not self.db_pool:
            return None
        
        async with self.db_pool.acquire() as conn:
            sql = """
                SELECT id, name, ticker_symbol, industry, sector, market_cap, 
                       employees, founded_year, headquarters, website, description,
                       created_at, updated_at
                FROM companies 
                WHERE id = $1
            """
            row = await conn.fetchrow(sql, company_id)
            return dict(row) if row else None
    
    async def get_company_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company details by ticker symbol."""
        if not self.db_pool:
            return None
        
        async with self.db_pool.acquire() as conn:
            sql = """
                SELECT id, name, ticker_symbol, industry, sector, market_cap, 
                       employees, founded_year, headquarters, website, description,
                       created_at, updated_at
                FROM companies 
                WHERE ticker_symbol = $1
            """
            row = await conn.fetchrow(sql, ticker.upper())
            return dict(row) if row else None
    
    async def run(self):
        """Run the MCP server."""
        await self.initialize_database()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="database-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point."""
    server = DatabaseServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())