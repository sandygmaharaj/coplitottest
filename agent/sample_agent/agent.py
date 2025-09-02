"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from copilotkit import CopilotKitState
from .perplexity_client import CompanyResearchClient

class AgentState(CopilotKitState):
    """
    Here we define the state of the agent

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're adding custom fields for company information.
    """
    companies: List[Dict[str, Any]] = []
    selected_company: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None
    research_data: Optional[Dict[str, Any]] = None
    is_researching: bool = False
    pending_tool_calls: List[Dict[str, Any]] = []
    awaiting_approval: bool = False

# Initialize company research client (OpenAI-powered)
research_client = CompanyResearchClient()

@tool
async def search_companies_db(query: str, limit: int = 10) -> str:
    """
    Search for companies in the PostgreSQL database by name or ticker symbol.
    
    Args:
        query: Company name or ticker symbol to search for
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string with company information from database
    """
    try:
        print(f"🔍 Searching companies database for: {query}")
        # In a real implementation, you'd connect to your MCP server here
        # For now, we'll return mock data that matches our database schema
        mock_results = [
            {
                "id": 1,
                "name": "Apple Inc.",
                "ticker_symbol": "AAPL",
                "industry": "Consumer Electronics",
                "sector": "Technology",
                "market_cap": 3000000000000,
                "employees": 164000,
                "founded_year": 1976,
                "headquarters": "Cupertino, CA",
                "website": "https://www.apple.com",
                "description": "Apple Inc. is an American multinational technology company specializing in consumer electronics, software, and online services."
            },
            {
                "id": 2,
                "name": "Microsoft Corporation",
                "ticker_symbol": "MSFT",
                "industry": "Software",
                "sector": "Technology",
                "market_cap": 2800000000000,
                "employees": 221000,
                "founded_year": 1975,
                "headquarters": "Redmond, WA",
                "website": "https://www.microsoft.com",
                "description": "Microsoft Corporation is an American multinational technology corporation."
            },
            {
                "id": 3,
                "name": "Tesla Inc.",
                "ticker_symbol": "TSLA",
                "industry": "Electric Vehicles",
                "sector": "Consumer Discretionary",
                "market_cap": 800000000000,
                "employees": 140000,
                "founded_year": 2003,
                "headquarters": "Austin, TX",
                "website": "https://www.tesla.com",
                "description": "Tesla, Inc. is an American electric vehicle and clean energy company."
            }
        ]
        
        # Filter results based on query
        filtered_results = [
            result for result in mock_results 
            if query.lower() in result["name"].lower() or 
               query.upper() in result["ticker_symbol"]
        ]
        
        print(f"📊 Found {len(filtered_results)} companies matching '{query}'")
        result_json = json.dumps(filtered_results[:limit], indent=2)
        print(f"📤 Returning data: {result_json}")
        return result_json
    except Exception as e:
        return json.dumps({"error": f"Database search failed: {str(e)}"}, indent=2)

@tool
async def search_company_openai(company_name: str, specific_info: str = None) -> str:
    """
    Search for company information using OpenAI.
    
    Args:
        company_name: Name of the company to search for
        specific_info: Specific information to look for (e.g., "recent news", "financial performance")
    
    Returns:
        JSON string with company information from OpenAI
    """
    try:
        result = await research_client.search_company_info(company_name, specific_info)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"OpenAI search failed: {str(e)}"}, indent=2)

@tool
async def get_company_news(company_name: str, days: int = 7) -> str:
    """
    Get recent news about a company using OpenAI.
    
    Args:
        company_name: Name of the company
        days: Number of days to look back for news (default: 7)
    
    Returns:
        JSON string with recent news
    """
    try:
        result = await research_client.get_company_news(company_name, days)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"News search failed: {str(e)}"}, indent=2)

@tool
async def get_company_financials(company_name: str) -> str:
    """
    Get financial information about a company using OpenAI.
    
    Args:
        company_name: Name of the company
    
    Returns:
        JSON string with financial information
    """
    try:
        result = await research_client.get_company_financials(company_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Financial search failed: {str(e)}"}, indent=2)

@tool
async def compare_companies(company1: str, company2: str) -> str:
    """
    Compare two companies using OpenAI.
    
    Args:
        company1: Name of the first company
        company2: Name of the second company
    
    Returns:
        JSON string with comparison results
    """
    try:
        result = await research_client.compare_companies(company1, company2)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Comparison failed: {str(e)}"}, indent=2)

tools = [
    search_companies_db,
    search_company_openai,
    get_company_news,
    get_company_financials,
    compare_companies
]

async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    Standard chat node based on the ReAct design pattern. It handles:
    - The model to use (and binds in CopilotKit actions and the tools defined above)
    - The system prompt
    - Getting a response from the model
    - Handling tool calls

    For more about the ReAct design pattern, see: 
    https://www.perplexity.ai/search/react-agents-NcXLQhreS0WDzpVaS4m9Cg
    """
    
    print("🤖 Chat node called with state keys:", list(state.keys()))
    print("🤖 Messages count:", len(state.get("messages", [])))
    print("🤖 Available actions:", [action.get("name") for action in state.get("copilotkit", {}).get("actions", [])])
    if state.get("messages"):
        print("🤖 Last message:", state["messages"][-1].content if state["messages"] else "No messages")
    
    # 1. Define the model
    model = ChatOpenAI(model="gpt-4o")

    # 2. Bind the tools to the model
    model_with_tools = model.bind_tools(
        [
            *state["copilotkit"]["actions"],
            *tools
        ],

        # 2.1 Disable parallel tool calls to avoid race conditions,
        #     enable this for faster performance if you want to manage
        #     the complexity of running tool calls in parallel.
        parallel_tool_calls=False,
    )

    # 3. Define the system message by which the chat model will be run
    system_message = SystemMessage(
        content=f"""You are a helpful company research assistant. You have access to:
        
        1. A PostgreSQL database with company information (use search_companies_db tool)
        2. OpenAI-powered research tools for comprehensive company analysis
        3. Frontend actions to display company information and stream research results
        
        WORKFLOW - When users ask about companies, follow this exact order:
        
        1. ALWAYS start by calling search_companies_db tool to get basic company info
        2. If search_companies_db returns company data:
           - Call displayCompanyInfo with the first company found
           - If multiple companies found, also call updateCompanyList
        3. Call startResearch with the company name to indicate research is beginning
        4. THEN stream OpenAI research results in sequence:
           - Call search_company_openai for detailed business analysis
           - Call updateResearchAnalysis with the analysis content
           - Call get_company_news for recent news and developments
           - Call updateResearchNews with the news content
           - Call get_company_financials for financial performance
           - Call updateResearchFinancials with the financial content (this also ends research)
        5. Provide a comprehensive response combining both database and OpenAI research
        
        CRITICAL RULES:
        - ALWAYS call search_companies_db FIRST for any company query
        - ALWAYS call displayCompanyInfo or updateCompanyList with the database results
        - ALWAYS call startResearch before beginning OpenAI research
        - ALWAYS stream research results using updateResearchAnalysis, updateResearchNews, updateResearchFinancials
        - Call updateResearchFinancials LAST to end the research state
        - If a tool returns an error, try the next available tool
        - Never give up without trying both database and OpenAI research
        
        Example for "Show me Apple":
        1. Call search_companies_db with query="Apple"
        2. Parse the JSON result and call displayCompanyInfo with the company object (NOT the JSON string)
        3. Call startResearch with company_name="Apple Inc."
        4. Call search_company_openai with company_name="Apple Inc." for detailed analysis
        5. Call updateResearchAnalysis with the analysis content
        6. Call get_company_news with company_name="Apple Inc." for recent news
        7. Call updateResearchNews with the news content
        8. Call get_company_financials with company_name="Apple Inc." for financial data
        9. Call updateResearchFinancials with the financial content
        10. Provide comprehensive response combining all sources
        
        IMPORTANT: When calling displayCompanyInfo or updateCompanyList, pass the actual company object(s), NOT the JSON string from the database tool.
        
        CRITICAL JSON HANDLING:
        - When search_companies_db returns a JSON string, you MUST parse it first before calling frontend actions
        - Extract individual company objects from the parsed JSON array
        - Pass these objects directly to displayCompanyInfo/updateCompanyList
        - DO NOT pass the raw JSON string to frontend actions
        
        MANDATORY: For every company query, you MUST call BOTH database AND OpenAI tools.
        Database gives basic info, OpenAI provides comprehensive analysis, news, and financials.
        STREAMING: Always use the streaming frontend actions to display research results as they come in.
        
        Talk in {state.get('language', 'english')}."""
    )

    # 4. Run the model to generate a response
    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)
    
    print("🤖 Model response type:", type(response))
    print("🤖 Model response has tool_calls:", hasattr(response, 'tool_calls') and bool(response.tool_calls))
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print("🤖 Tool calls:", [tc.get("name") for tc in response.tool_calls])

    # 5. Check for tool calls in the response and handle them. We ignore
    #    CopilotKit actions, as they are handled by CopilotKit.
    if isinstance(response, AIMessage) and response.tool_calls:
        actions = state["copilotkit"]["actions"]
        
        # Debug: Print what action is being called and with what arguments
        for tool_call in response.tool_calls:
            if tool_call.get("name") in ["displayCompanyInfo", "updateCompanyList", "startResearch", "updateResearchAnalysis", "updateResearchNews", "updateResearchFinancials"]:
                print(f"🎯 Agent calling frontend action: {tool_call.get('name')}")
                print(f"🎯 With arguments: {tool_call.get('args', {})}")

        # 5.1 Check for any non-copilotkit actions in the response and
        #     request human approval before executing them.
        non_copilotkit_calls = [
            tc for tc in response.tool_calls 
            if not any(action.get("name") == tc.get("name") for action in actions)
        ]
        
        if non_copilotkit_calls:
            # Create human-readable descriptions for approval
            tool_descriptions = []
            for tool_call in non_copilotkit_calls:
                tool_name = tool_call.get('name')
                tool_args = tool_call.get('args', {})
                
                if tool_name == 'search_companies_db':
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Search database for companies matching: '{tool_args.get('query', '')}'",
                        "args": tool_args
                    })
                elif tool_name == 'search_company_openai':
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Get AI analysis for company: '{tool_args.get('company_name', '')}'",
                        "args": tool_args
                    })
                elif tool_name == 'get_company_news':
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Get recent news for company: '{tool_args.get('company_name', '')}'",
                        "args": tool_args
                    })
                elif tool_name == 'get_company_financials':
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Get financial data for company: '{tool_args.get('company_name', '')}'",
                        "args": tool_args
                    })
                elif tool_name == 'compare_companies':
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Compare companies: '{tool_args.get('company1', '')}' vs '{tool_args.get('company2', '')}'",
                        "args": tool_args
                    })
                else:
                    tool_descriptions.append({
                        "name": tool_name,
                        "description": f"Execute {tool_name} with args: {tool_args}",
                        "args": tool_args
                    })
            
            # For now, disable human-in-the-loop to avoid OpenAI API conflicts
            # Log what would be requested for approval
            print(f"🚨 Would request approval for: {[desc['description'] for desc in tool_descriptions]}")
            print("🚨 Proceeding with execution (human-in-the-loop temporarily disabled)")
            
            # Just proceed with tool execution for now
            return Command(goto="tool_node", update={"messages": response})

    # 6. We've handled all tool calls, so we can end the graph.
    return Command(
        goto=END,
        update={
            "messages": response
        }
    )

# Disabled - using simplified approval approach
# async def human_approval_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Human approval node that asks for confirmation before executing tools.
    """
    print("👤 Human approval node called")
    print(f"👤 Pending tool calls: {[tc.get('name') for tc in state.get('pending_tool_calls', [])]}")
    
    if not state.get('pending_tool_calls'):
        print("👤 No pending tool calls, ending")
        return {**state, "awaiting_approval": False}
    
    # Create a human-readable description of the tools to be executed
    tool_descriptions = []
    for tool_call in state.get('pending_tool_calls', []):
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('args', {})
        
        if tool_name == 'search_companies_db':
            tool_descriptions.append(f"Search database for companies matching: '{tool_args.get('query', '')}'")
        elif tool_name == 'search_company_openai':
            tool_descriptions.append(f"Get AI analysis for company: '{tool_args.get('company_name', '')}'")
        elif tool_name == 'get_company_news':
            tool_descriptions.append(f"Get recent news for company: '{tool_args.get('company_name', '')}'")
        elif tool_name == 'get_company_financials':
            tool_descriptions.append(f"Get financial data for company: '{tool_args.get('company_name', '')}'")
        elif tool_name == 'compare_companies':
            tool_descriptions.append(f"Compare companies: '{tool_args.get('company1', '')}' vs '{tool_args.get('company2', '')}'")
        else:
            tool_descriptions.append(f"Execute {tool_name} with args: {tool_args}")
    
    # Create approval message
    approval_message = f"""🤖 I need your approval to execute the following tools:

{chr(10).join(f'• {desc}' for desc in tool_descriptions)}

Please respond with:
- "approve" or "yes" to proceed
- "deny" or "no" to cancel"""
    
    approval_msg = AIMessage(content=approval_message)
    
    # Return state with approval message and interrupt for human input
    return {
        **state,
        "messages": state.get("messages", []) + [approval_msg],
        "awaiting_approval": True
    }

async def check_approval_node(state: AgentState, config: RunnableConfig) -> Command[Literal["tool_node", "chat_node", "__end__"]]:
    """
    Check the human's approval response.
    """
    print("✅ Check approval node called")
    
    if not state.get('messages'):
        print("✅ No messages, ending")
        return Command(goto=END, update={"awaiting_approval": False})
    
    # Get the last human message (should be the response to our approval request)
    last_message = state['messages'][-1]
    if hasattr(last_message, 'content'):
        response_content = last_message.content.lower().strip()
        print(f"✅ Human response: '{response_content}'")
        
        # Check approval
        if any(word in response_content for word in ['approve', 'yes', 'proceed', 'ok', 'continue']):
            print("✅ Human approved, proceeding to tool execution")
            # Create a new AIMessage with the original tool calls
            tool_message = AIMessage(content="Executing approved tools...", tool_calls=state.get('pending_tool_calls', []))
            return Command(
                goto="tool_node",
                update={
                    "messages": state.get("messages", []) + [tool_message],
                    "awaiting_approval": False,
                    "pending_tool_calls": []
                }
            )
        elif any(word in response_content for word in ['deny', 'no', 'cancel', 'stop']):
            print("❌ Human denied, cancelling tool execution")
            cancel_message = AIMessage(content="Tool execution cancelled as per your request. How else can I help you?")
            return Command(
                goto=END,
                update={
                    "messages": state.get("messages", []) + [cancel_message],
                    "awaiting_approval": False,
                    "pending_tool_calls": []
                }
            )
        else:
            print("❓ Unclear response, asking for clarification")
            clarification_message = AIMessage(content="I didn't understand your response. Please reply with 'approve' to proceed or 'deny' to cancel.")
            return Command(
                goto="chat_node",
                update={
                    "messages": state.get("messages", []) + [clarification_message],
                    "awaiting_approval": True
                }
            )
    
    print("❓ No valid message content, ending")
    return Command(goto=END, update={"awaiting_approval": False})

# Define the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")

# Compile the workflow graph with checkpointer
checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
