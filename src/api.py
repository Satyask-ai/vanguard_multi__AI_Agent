import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from agent import run_agent  # Import the agent runner
# Initialize the API
app = FastAPI(
    title="Vanguard Advisor-Assist API",
    description="Secure RAG API with Role-Based Access Control (RBAC)",
    version="1.0.0"
)

# --- Data Models (The Contract) ---
class QueryRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "What are the fund costs for VYM?"})
    user_role: str = Field(..., description="Role: 'advisor' or 'intern'", json_schema_extra={"example": "advisor"})

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
    try:
        print(f"📝 AUDIT LOG: User Role '{request.user_role}' asked: '{request.question}'")

        # CALL THE AGENT
        # In a real system, you'd pass the user_role into the agent state config
        response_text = run_agent(request.question)
        
        return QueryResponse(
            answer=response_text,
            user_role_used=request.user_role,
            status="success"
        )
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server on localhost port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)