"""
OpenAI client for company information search and analysis.
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Any
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class CompanyResearchClient:
    """Client for OpenAI-powered company research."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def search_company_info(self, company_name: str, specific_info: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for company information using OpenAI.
        
        Args:
            company_name: Name of the company to search for
            specific_info: Specific information to look for (e.g., "recent news", "financial performance")
        
        Returns:
            Dictionary containing the search results
        """
        if not self.api_key:
            return {"error": "OpenAI API key not configured"}
        
        # Construct the search query
        if specific_info:
            prompt = f"""Provide comprehensive information about {company_name} company, focusing on: {specific_info}.

Please include:
- Business overview and key products/services
- Recent news and developments
- Financial performance indicators
- Market position and competitive landscape
- Key leadership and management
- Recent strategic initiatives

Format the response as detailed, factual information that would be useful for business research."""
        else:
            prompt = f"""Provide comprehensive information about {company_name} company.

Please include:
- Business overview and key products/services
- Recent news and major developments (last 6 months)
- Financial performance and key metrics
- Market position and competitive landscape
- Key leadership and management team
- Strategic initiatives and future outlook
- Any recent partnerships, acquisitions, or major announcements

Format the response as detailed, factual information that would be useful for business research."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate information about companies. Focus on factual data including business overview, recent developments, financial information, and market analysis. Be comprehensive but concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            return self._process_response(content, company_name)
        
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}
    
    def _process_response(self, content: str, company_name: str) -> Dict[str, Any]:
        """Process the API response into a structured format."""
        try:
            return {
                "company_name": company_name,
                "content": content,
                "source": "openai_gpt4o",
                "timestamp": None  # OpenAI doesn't provide timestamps in the same way
            }
        
        except Exception as e:
            logger.error(f"Error processing OpenAI response: {e}")
            return {"error": "Failed to process API response"}
    
    async def get_company_news(self, company_name: str, days: int = 7) -> Dict[str, Any]:
        """Get recent news about a company."""
        return await self.search_company_info(
            company_name,
            f"recent news and developments in the last {days} days"
        )
    
    async def get_company_financials(self, company_name: str) -> Dict[str, Any]:
        """Get financial information about a company."""
        return await self.search_company_info(
            company_name,
            "financial performance, revenue, profits, stock price, and market cap"
        )
    
    async def get_company_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get business analysis and market position of a company."""
        return await self.search_company_info(
            company_name,
            "business strategy, competitive position, market analysis, and industry trends"
        )
    
    async def compare_companies(self, company1: str, company2: str) -> Dict[str, Any]:
        """Compare two companies."""
        prompt = f"""Compare {company1} and {company2} companies in detail.

Please provide a comprehensive comparison including:
- Business models and core products/services
- Financial performance and market capitalization
- Market position and competitive advantages
- Revenue streams and profitability
- Growth strategies and future outlook
- Strengths and weaknesses of each company
- Market share and competitive landscape

Format the response as a detailed comparative analysis."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides detailed comparisons between companies. Focus on factual data and objective analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            return self._process_response(content, f"{company1} vs {company2}")
        
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}

# Example usage for testing
async def test_perplexity_client():
    """Test the Perplexity client."""
    client = PerplexityClient()
    
    # Test company search
    result = await client.search_company_info("Apple Inc.")
    print("Company Info:", json.dumps(result, indent=2))
    
    # Test news search
    news = await client.get_company_news("Tesla", days=30)
    print("News:", json.dumps(news, indent=2))

if __name__ == "__main__":
    asyncio.run(test_perplexity_client())