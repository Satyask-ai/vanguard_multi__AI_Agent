import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_chroma import Chroma


load_dotenv()

# CONFIG: Enterprise Switch
# Checks if Azure keys exist; otherwise falls back to standard OpenAI
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

if azure_api_key and azure_api_key != "placeholder_key":
    print("Using Azure OpenAI Embeddings (Production Mode)")
    if not azure_endpoint:
        raise ValueError("Azure Endpoint is missing in .env")
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        openai_api_version="2023-05-15",
        azure_endpoint=azure_endpoint
    )
else:
    print("Using Standard OpenAI Embeddings (Dev Mode)")
    embeddings = OpenAIEmbeddings()

VECTOR_DB_PATH = "./chroma_db"

def ingest_documents():
    print("Starting Ingestion Process")
    
    # 1. Load the specific PDF you uploaded
    pdf_path = "./data/fund_report_2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        print("Please ensure 'fund_report_2024.pdf' is in the 'data' folder.")
        return

    # PDFPlumber is great for extracting text from these Vanguard tables
    loader = PDFPlumberLoader(pdf_path)
    raw_docs = loader.load()
    print(f"Loaded {len(raw_docs)} pages.")

    # 2. Add Metadata (The 'Security' Layer)
    # We tag this as VYM (High Dividend Yield) and Year 2025 based on your PDF
    for doc in raw_docs:
        doc.metadata["access_level"] = "confidential"  # Security Tag
        doc.metadata["fund_id"] = "VYM"
        doc.metadata["year"] = 2025
        doc.metadata["source"] = "Vanguard High Dividend Yield Index Fund Annual Report"

    # 3. Chunking
    # Overlap 200 tokens to keep "Sector Allocation" headers connected to the data
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(raw_docs)
    print(f"Split into {len(chunks)} chunks.")

    # 4. Embed & Store
    print("Saving to Vector Database")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    print("Ingestion Complete! Vectors stored in ./chroma_db")

if __name__ == "__main__":
    ingest_documents()