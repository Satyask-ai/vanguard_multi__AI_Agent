import math
from langchain_core.tools import tool
from rag_engine import get_rag_chain

# --- TOOL 1: The Researcher (Your RAG System) ---
@tool
def research_fund_reports(query: str):
    """
    Use this tool to find qualitative information from internal Vanguard reports.
    Useful for questions about risks, outlooks, fees, or fund strategy.
    """
    # We default to 'advisor' role for the agent's research
    # In a real app, you'd pass the user_role into the tool context
    chain = get_rag_chain("advisor") 
    response = chain.invoke(query)
    return response

# --- TOOL 2: The Calculator (Deterministic Math) ---
@tool
def calculate_investment_growth(principal: float, rate_decimal: float, years: int):
    """
    Calculates the future value of an investment using compound interest.
    - principal: The starting amount (e.g., 10000)
    - rate_decimal: The annual return rate as a decimal (e.g., 0.07 for 7%)
    - years: Number of years to grow
    """
    amount = principal * math.pow((1 + rate_decimal), years)
    return f"${amount:,.2f}"