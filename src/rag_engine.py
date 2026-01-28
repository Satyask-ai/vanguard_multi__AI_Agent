import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI, AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

# ==========================================
# 1. SETUP: Enterprise Switch
# ==========================================
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

if azure_api_key and azure_api_key != "placeholder_key":
    print("RAG Engine: Using Azure OpenAI (Production)")
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        openai_api_version="2023-05-15",
        azure_endpoint=azure_endpoint
    )
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_GPT4_DEPLOYMENT"),
        openai_api_version="2023-05-15",
        azure_endpoint=azure_endpoint,
        temperature=0
    )
else:
    print("RAG Engine: Using Standard OpenAI (Dev)")
    embeddings = OpenAIEmbeddings()
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# ==========================================
# 2. PROMPT ENGINEERING
# ==========================================
template = """
You are a Vanguard Investment Research Assistant. 
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "Information not available in internal reports."
Do not guess. 

Format your answer cleanly. If there are financial figures, use bullet points.
ALWAYS cite the 'source' and 'Year' from the metadata.

Context:
{context}

Question:
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}, Year: {d.metadata.get('year', 'N/A')}] \nContent: {d.page_content}" for d in docs])

# ==========================================
# 3. RETRIEVAL LOGIC (Security Layer)
# ==========================================
def get_rag_chain(user_role: str):
    
    # SECURITY FILTER
    search_kwargs = {"k": 3}
    
    if user_role == "intern":
        # Interns CANNOT see confidential docs
        search_kwargs["filter"] = {"access_level": {"$ne": "confidential"}}
        print(f"Security Alert: Restrictions applied for '{user_role}'")
    else:
        print(f"Access Granted: Full visibility for '{user_role}'")
    
    retriever = vector_db.as_retriever(search_kwargs=search_kwargs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain