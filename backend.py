import os
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.search.documents.indexes.models import ScoringProfile

# Azure Configuration
AZURE_OPENAI_ENDPOINT = "https://oai-z-autosol-revamp-n-002.openai.azure.com/openai/deployments/gpt40/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_API_KEY = "RSURy9Zwtj3DAQGnSQJX3w3AAABACG0QQ2Y"
AZURE_API_VERSION = "2025-01-01-preview"

VECTOR_STORE_ADDRESS = "https://rivovarch.windows.net"
VECTOR_STORE_PASSWORD = "PLESJ4h1jT7nGyW0BQ34QHqTVW8A5Yo7ZxBTi8"

# Initialize Embeddings
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Setup Vector Store
vector_store = AzureSearch(
    azure_search_endpoint=VECTOR_STORE_ADDRESS,
    azure_search_key=VECTOR_STORE_PASSWORD,
    index_name="helpdesk-index",
    embedding_function=embeddings.embed_query
)

# Initialize Azure OpenAI Chat Model
llm = AzureChatOpenAI(
    azure_deployment="gpt40",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_API_VERSION
)

# Function to get response from RAG
def get_response(question):
    # Perform similarity search
    docs = vector_store.similarity_search(question, k=12, search_type="hybrid")
    context = "\n".join([doc.page_content for doc in docs])

    # Chat Prompt
    prompt = f"You are a helpful assistant that answers the question based on the context.\nContext:\n{context}\nQuestion: {question}"
    
    response = llm.invoke({"question": question, "context": context})
    return response.content
