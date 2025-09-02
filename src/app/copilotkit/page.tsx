"use client";

import { useCoAgent, useCopilotAction, CopilotKit } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";
import { useState } from "react";

export default function CopilotKitPage() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="sample_agent">
      <CopilotKitContent />
    </CopilotKit>
  );
}

function CopilotKitContent() {
  return (
    <div className="min-h-screen bg-background text-foreground flex">
      <div className="flex-1">
        <YourMainContent />
      </div>
      <CopilotSidebar
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "Company Research Assistant",
          initial: "👋 Hi! I'm your company research assistant. I can help you find information about companies using both database records and real-time AI analysis.\n\nFor example you can try:\n- **Database Search**: \"Show me information about Apple\"\n- **Real-time Analysis**: \"What's the latest news about Tesla?\"\n- **Company Comparison**: \"Compare Microsoft and Google\"\n- **Financial Data**: \"What are Amazon's recent financials?\"\n\nAs you interact with me, you'll see a dynamic canvas appear with company information, news, and comprehensive analysis."
        }}
      />
    </div>
  );
}

// State of the agent, make sure this aligns with your agent's state.
type AgentState = {
  companies: Array<{
    id: number;
    name: string;
    ticker_symbol: string;
    industry: string;
    sector: string;
    market_cap: number;
    employees: number;
    founded_year: number;
    headquarters: string;
    website: string;
    description: string;
  }>;
  selected_company?: {
    id: number;
    name: string;
    ticker_symbol: string;
    industry: string;
    sector: string;
    market_cap: number;
    employees: number;
    founded_year: number;
    headquarters: string;
    website: string;
    description: string;
  };
  search_results?: any;
  research_data?: {
    analysis?: string;
    news?: string;
    financials?: string;
    comparison?: string;
  };
  is_researching?: boolean;
  awaiting_approval?: boolean;
  pending_tool_calls?: Array<{
    name: string;
    args: any;
  }>;
}

function YourMainContent() {
  // 🪁 Shared State: https://docs.copilotkit.ai/coagents/shared-state
  const {state, setState} = useCoAgent<AgentState>({
    name: "sample_agent",
    initialState: {
      companies: [],
      selected_company: undefined,
      search_results: undefined,
      research_data: undefined,
      is_researching: false,
      awaiting_approval: false,
      pending_tool_calls: [],
    },
  })
  
  console.log("🔍 Current agent state:", state);

  // 🪁 Frontend Actions: https://docs.copilotkit.ai/coagents/frontend-actions
  useCopilotAction({
    name: "displayCompanyInfo",
    parameters: [{
      name: "company",
      description: "Company information to display",
      required: true,
    }],
    handler: ({ company }) => {
      console.log("🎯 displayCompanyInfo called with raw:", company);
      
      // Parse company data if it's a JSON string
      let parsedCompany;
      try {
        parsedCompany = typeof company === 'string' ? JSON.parse(company) : company;
      } catch (e) {
        console.error("Failed to parse company data:", e);
        parsedCompany = company;
      }
      
      console.log("🎯 Parsed company data:", parsedCompany);
      console.log("🎯 Current state before update:", state);
      const newState = {
        ...state,
        selected_company: parsedCompany,
      };
      console.log("🎯 New state to set:", newState);
      setState(newState);
    },
  });

  useCopilotAction({
    name: "updateCompanyList",
    parameters: [{
      name: "companies",
      description: "List of companies to display",
      required: true,
    }],
    handler: ({ companies }) => {
      console.log("🎯 updateCompanyList called with raw:", companies);
      
      // Parse companies data if it's a JSON string
      let parsedCompanies;
      try {
        parsedCompanies = typeof companies === 'string' ? JSON.parse(companies) : companies;
      } catch (e) {
        console.error("Failed to parse companies data:", e);
        parsedCompanies = companies;
      }
      
      console.log("🎯 Parsed companies data:", parsedCompanies);
      setState({
        ...state,
        companies: parsedCompanies,
      });
    },
  });

  // Tool approval action
  useCopilotAction({
    name: "requestToolApproval",
    parameters: [{
      name: "tool_descriptions",
      description: "List of tools to be executed with descriptions",
      required: true,
    }],
    handler: ({ tool_descriptions }) => {
      console.log("👤 Tool approval requested for:", tool_descriptions);
      
      // Parse tool descriptions if it's a JSON string
      let parsedDescriptions;
      try {
        parsedDescriptions = typeof tool_descriptions === 'string' ? JSON.parse(tool_descriptions) : tool_descriptions;
      } catch (e) {
        console.error("Failed to parse tool descriptions:", e);
        parsedDescriptions = tool_descriptions;
      }
      
      setState({
        ...state,
        awaiting_approval: true,
        pending_tool_calls: parsedDescriptions,
      });
    },
  });

  // Research data streaming actions
  useCopilotAction({
    name: "startResearch",
    parameters: [{
      name: "company_name",
      description: "Name of the company being researched",
      required: true,
    }],
    handler: ({ company_name }) => {
      console.log("🔬 Starting research for:", company_name);
      setState({
        ...state,
        is_researching: true,
        research_data: undefined,
      });
    },
  });

  useCopilotAction({
    name: "updateResearchAnalysis",
    parameters: [{
      name: "analysis",
      description: "OpenAI company analysis content",
      required: true,
    }],
    handler: ({ analysis }) => {
      console.log("📊 Received analysis data");
      setState({
        ...state,
        research_data: {
          ...state.research_data,
          analysis: typeof analysis === 'string' ? analysis : JSON.stringify(analysis),
        },
      });
    },
  });

  useCopilotAction({
    name: "updateResearchNews",
    parameters: [{
      name: "news",
      description: "OpenAI company news content",
      required: true,
    }],
    handler: ({ news }) => {
      console.log("📰 Received news data");
      setState({
        ...state,
        research_data: {
          ...state.research_data,
          news: typeof news === 'string' ? news : JSON.stringify(news),
        },
      });
    },
  });

  useCopilotAction({
    name: "updateResearchFinancials",
    parameters: [{
      name: "financials",
      description: "OpenAI company financial content",
      required: true,
    }],
    handler: ({ financials }) => {
      console.log("💰 Received financial data");
      setState({
        ...state,
        research_data: {
          ...state.research_data,
          financials: typeof financials === 'string' ? financials : JSON.stringify(financials),
        },
        is_researching: false,
      });
    },
  });

  //🪁 Generative UI: https://docs.copilotkit.ai/coagents/generative-ui
  useCopilotAction({
    name: "showCompanyCard",
    description: "Display a company information card.",
    available: "disabled",
    parameters: [
      { name: "company", type: "object", required: true },
    ],
    render: ({ args }) => {
      return <CompanyCard company={args.company} />
    },
  });

  // Show canvas only when there's content to display
  const showCanvas = state.selected_company || state.companies?.length > 0 || state.research_data || state.is_researching || state.awaiting_approval;

  if (!showCanvas) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-4">Company Research Canvas</h1>
          <p className="text-muted-foreground text-lg">
            Start a conversation to explore comprehensive company analysis
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">Company Research Canvas</h1>
          <p className="text-muted-foreground mt-2">Live analysis and insights</p>
        </div>
        
        {/* Selected Company Display */}
        {state.selected_company && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Company Overview</h2>
            <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="space-y-1">
                    <h3 className="text-2xl font-semibold">{state.selected_company.name}</h3>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80">
                        {state.selected_company.ticker_symbol}
                      </span>
                      <span className="text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground">{state.selected_company.sector}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">
                      ${(state.selected_company.market_cap / 1000000000).toFixed(1)}B
                    </div>
                    <div className="text-sm text-muted-foreground">Market Cap</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Industry</div>
                    <div className="font-medium">{state.selected_company.industry}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Employees</div>
                    <div className="font-medium">{state.selected_company.employees?.toLocaleString()}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Founded</div>
                    <div className="font-medium">{state.selected_company.founded_year}</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground">Headquarters</div>
                  <div className="font-medium">{state.selected_company.headquarters}</div>
                </div>
                
                <div className="mt-6 pt-6 border-t">
                  <div className="text-sm text-muted-foreground mb-2">About</div>
                  <p className="text-sm leading-relaxed">{state.selected_company.description}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tool Approval Status */}
        {state.awaiting_approval && (
          <div className="mb-8">
            <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="animate-pulse rounded-full h-4 w-4 bg-yellow-500"></div>
                  <span className="text-sm font-medium">Tool Execution Approval Required</span>
                </div>
                
                {/* Tool descriptions */}
                {state.pending_tool_calls && state.pending_tool_calls.length > 0 && (
                  <div className="mb-4">
                    <div className="text-sm font-medium mb-2">The following tools will be executed:</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {state.pending_tool_calls.map((tool, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-primary">•</span>
                          <span>{tool.description || tool.name}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="flex gap-3">
                  <button
                    onClick={async () => {
                      console.log("✅ User approved tool execution");
                      setState({
                        ...state,
                        awaiting_approval: false,
                        pending_tool_calls: [],
                      });
                      // Send approval message to continue agent execution
                      // We'll need to implement a way to trigger agent continuation
                      console.log("Approval granted - agent should continue with tool execution");
                    }}
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                  >
                    ✅ Approve
                  </button>
                  <button
                    onClick={async () => {
                      console.log("❌ User denied tool execution");
                      setState({
                        ...state,
                        awaiting_approval: false,
                        pending_tool_calls: [],
                      });
                      // Send denial message
                      console.log("Approval denied - tools will not be executed");
                    }}
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
                  >
                    ❌ Deny
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Research Status */}
        {state.is_researching && (
          <div className="mb-8">
            <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
              <div className="p-6">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  <span className="text-sm font-medium">Conducting comprehensive research...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Research Results */}
        {state.research_data && (
          <div className="space-y-8">
            {state.research_data.analysis && (
              <div>
                <h2 className="text-2xl font-semibold mb-4">📊 Business Analysis</h2>
                <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
                  <div className="p-6">
                    <div className="prose prose-sm max-w-none">
                      <ResearchContent content={state.research_data.analysis} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {state.research_data.news && (
              <div>
                <h2 className="text-2xl font-semibold mb-4">📰 Recent News & Developments</h2>
                <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
                  <div className="p-6">
                    <div className="prose prose-sm max-w-none">
                      <ResearchContent content={state.research_data.news} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {state.research_data.financials && (
              <div>
                <h2 className="text-2xl font-semibold mb-4">💰 Financial Analysis</h2>
                <div className="border rounded-lg bg-card text-card-foreground shadow-sm">
                  <div className="p-6">
                    <div className="prose prose-sm max-w-none">
                      <ResearchContent content={state.research_data.financials} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Company List */}
        {state.companies?.length > 0 && !state.selected_company && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Companies Found</h2>
            <div className="grid gap-4">
              {state.companies.map((company, index) => (
                <div 
                  key={company.id || index} 
                  className="border rounded-lg bg-card text-card-foreground shadow-sm hover:shadow-md transition-all cursor-pointer hover:border-primary/50"
                  onClick={() => setState({
                    ...state,
                    selected_company: company,
                  })}
                >
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <h3 className="font-semibold">{company.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>{company.ticker_symbol}</span>
                          <span>•</span>
                          <span>{company.industry}</span>
                        </div>
                      </div>
                      <div className="text-right space-y-1">
                        <div className="font-semibold">
                          ${(company.market_cap / 1000000000).toFixed(1)}B
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {company.employees?.toLocaleString()} employees
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Simple building icon for the company card
function BuildingIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-muted-foreground">
      <path d="M3 21V8l5-5 5 5v13H3zm2-2h8v-2H5v2zm0-3h3v-2H5v2zm5 0h3v-2h-3v2zm0-3h3v-2h-3v2zm-5 0h3v-2H5v2z" />
    </svg>
  );
}

// Component for displaying research content with proper formatting
function ResearchContent({ content }: { content: string }) {
  if (!content) return null;
  
  // Split content into paragraphs and format
  const paragraphs = content.split('\n').filter(p => p.trim().length > 0);
  
  return (
    <div className="space-y-4">
      {paragraphs.map((paragraph, index) => {
        // Check if paragraph is a header (starts with #, -, or is all caps)
        const isHeader = paragraph.match(/^#+\s/) || paragraph.match(/^-+\s/) || 
                        (paragraph.length < 100 && paragraph === paragraph.toUpperCase());
        
        if (isHeader) {
          return (
            <h3 key={index} className="text-lg font-semibold text-primary mt-6 mb-3">
              {paragraph.replace(/^#+\s/, '').replace(/^-+\s/, '')}
            </h3>
          );
        }
        
        return (
          <p key={index} className="text-sm leading-relaxed text-foreground">
            {paragraph}
          </p>
        );
      })}
    </div>
  );
}

// Company card component for generative UI
function CompanyCard({ company }: { company?: any }) {
  if (!company) return null;
  
  return (
    <div className="border rounded-lg bg-card text-card-foreground shadow-sm mt-6 mb-4 max-w-md w-full">
      <div className="p-4">
        <div className="flex items-start justify-between mb-4">
          <div className="space-y-1">
            <h3 className="text-lg font-semibold">{company.name}</h3>
            <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80">
              {company.ticker_symbol}
            </span>
          </div>
          <BuildingIcon />
        </div>
        
        <div className="flex items-end justify-between mb-4">
          <div className="text-2xl font-bold">${(company.market_cap / 1000000000).toFixed(1)}B</div>
          <div className="text-sm text-muted-foreground">{company.industry}</div>
        </div>
        
        <div className="pt-4 border-t">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Employees</p>
              <p className="font-medium text-sm">{company.employees?.toLocaleString()}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Founded</p>
              <p className="font-medium text-sm">{company.founded_year}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Sector</p>
              <p className="font-medium text-sm">{company.sector}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
