import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from rag_engine import get_rag_chain

# Initialize the API
app = FastAPI(
    title="Vanguard Advisor-Assist API",
    description="Secure RAG API with Role-Based Access Control (RBAC)",
    version="1.0.0"
)

# --- Data Models (The Contract) ---
class QueryRequest(BaseModel):
    question: str = Field(..., example="What are the fund costs for VYM?")
    user_role: str = Field(..., example="advisor", description="Role: 'advisor' or 'intern'")

class QueryResponse(BaseModel):
    answer: str
    user_role_used: str
    status: str

# --- Endpoints ---
@app.get("/")
def health_check():
    return {"status": "running", "system": "Vanguard Advisor-Assist"}

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Main RAG Endpoint.
    - Advisors get full access.
    - Interns get restricted access.
    """
    try:
        # 1. Audit Logging (Simulated)
        print(f"📝 AUDIT LOG: User Role '{request.user_role}' asked: '{request.question}'")

        # 2. Get the Brain (configured for this specific role)
        chain = get_rag_chain(request.user_role)
        
        # 3. Generate Answer
        response_text = chain.invoke(request.question)
        
        return QueryResponse(
            answer=response_text,
            user_role_used=request.user_role,
            status="success"
        )
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI Error")

if __name__ == "__main__":
    # Run the server on localhost port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)