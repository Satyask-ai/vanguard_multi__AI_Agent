from src.rag_engine import get_rag_chain

print("--- TEST 1: Advisor Asking about VYM Costs ---")
# Advisor has access, should get the answer from Page 1 of your PDF ($6 for ETF Shares)
chain = get_rag_chain("advisor")
response = chain.invoke("What were the fund costs for VYM ETF Shares?")
print(f"🤖 AI Answer:\n{response}")

print("\n--- TEST 2: Intern Asking the same question ---")
# Intern has NO access to confidential docs, should be blocked
chain = get_rag_chain("intern")
response = chain.invoke("What were the fund costs for VYM ETF Shares?")
print(f"🤖 AI Answer:\n{response}")