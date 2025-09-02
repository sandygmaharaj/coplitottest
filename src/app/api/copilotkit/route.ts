import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  OpenAIAdapter,
  copilotKitEndpoint,
} from "@copilotkit/runtime";

const serviceAdapter = new OpenAIAdapter();

console.log("Environment variables:", {
  LANGGRAPH_DEPLOYMENT_URL: process.env.LANGGRAPH_DEPLOYMENT_URL,
  LANGSMITH_API_KEY: process.env.LANGSMITH_API_KEY,
  NEXT_PUBLIC_COPILOTKIT_AGENT_NAME: process.env.NEXT_PUBLIC_COPILOTKIT_AGENT_NAME,
  NEXT_PUBLIC_COPILOTKIT_AGENT_DESCRIPTION: process.env.NEXT_PUBLIC_COPILOTKIT_AGENT_DESCRIPTION
});

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    copilotKitEndpoint({
      url: `${process.env.LANGGRAPH_DEPLOYMENT_URL}/copilotkit`,
    }),
  ],
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
