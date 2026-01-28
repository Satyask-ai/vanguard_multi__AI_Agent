import os
from typing import TypedDict, Annotated, List
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages # <--- CRITICAL IMPORT
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from dotenv import load_dotenv
from tools import research_fund_reports, calculate_investment_growth

load_dotenv()

# 1. SETUP LLM
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
if azure_api_key and azure_api_key != "placeholder_key":
    print("🔹 Agent: Using Azure OpenAI")
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_GPT4_DEPLOYMENT"),
        openai_api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        temperature=0
    )
else:
    print("🔹 Agent: Using Standard OpenAI")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. BIND TOOLS
tools = [research_fund_reports, calculate_investment_growth]
llm_with_tools = llm.bind_tools(tools)

# 3. DEFINE STATE (FIXED MEMORY)
# We use 'add_messages' so the graph APPENDS to history instead of overwriting it.
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages] 

# 4. DEFINE NODES
def chatbot_node(state: AgentState):
    """The 'Brain' node that decides what to do."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 5. BUILD THE GRAPH
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("orchestrator", chatbot_node)
workflow.add_node("tools", ToolNode(tools))

# Add Edges
workflow.set_entry_point("orchestrator")
workflow.add_conditional_edges("orchestrator", tools_condition)
workflow.add_edge("tools", "orchestrator")

# Compile
agent_app = workflow.compile()

def run_agent(user_query: str):
    """Entry point for the API"""
    # Initialize with System Prompt + User Query
    initial_state = {"messages": [
        SystemMessage(content="You are a Vanguard Financial Planner. You have access to tools to research funds and calculate returns. Use 'research_fund_reports' to find data first, then 'calculate_investment_growth' if the user asks for projections."),
        HumanMessage(content=user_query)
    ]}
    
    # Run the graph
    result = agent_app.invoke(initial_state)
    return result["messages"][-1].content