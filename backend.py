import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_community.vectorstores.azure_search import AzureSearch
from azure.search.documents.indexes.models import SearchField, ScoringProfile

# Logging setup
logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://oai-z-autosol-revamp-n-002.openai.azure.com/"
AZURE_OPENAI_API_KEY = "RSUR9Zytwj3DAQngS0JX3w3AABAC0GQq2Y"
AZURE_OPENAI_DEPLOYMENT = "35k"  # Model deployment name
AZURE_OPENAI_API_VERSION = "2025-01-01-preview"

# Azure Search Configuration
VECTOR_SEARCH_ENDPOINT = "https://rivovarch.windows.net"
VECTOR_SEARCH_API_KEY = "PLESJ14hT1YnGrW9OB34qHk7WVBAsZ07xB1"
VECTOR_INDEX_NAME = "helpdesk-index"

# Initialize Azure OpenAI LLM
llm = AzureChatOpenAI(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Initialize Azure Search Vector Store
vector_store = AzureSearch(
    azure_search_endpoint=VECTOR_SEARCH_ENDPOINT,
    azure_search_key=VECTOR_SEARCH_API_KEY,
    index_name=VECTOR_INDEX_NAME
)

# Define the Chat Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers the {question} based on {context}. You also provide relevant follow-up questions."),
    ("human", "{question}")
])

@app.route("/chat", methods=["POST"])
def chat():
    """
    API Endpoint to process user queries and fetch responses using:
    - Azure OpenAI GPT-4 Turbo (35k)
    - Azure Search for RAG-based context retrieval
    """
    try:
        data = request.json
        user_question = data.get("question", "")

        if not user_question:
            return jsonify({"error": "Question is required"}), 400

        # Retrieve context from Azure Search
        search_results = vector_store.similarity_search(
            query=user_question,
            k=12,  # Retrieve top 12 most relevant documents
            search_type="hybrid"
        )

        # Combine retrieved context
        context = " ".join([doc.page_content for doc in search_results])

        # Generate response using Azure OpenAI
        chain = prompt | llm
        result = chain.invoke({"question": user_question, "context": context})

        # Extract response text and generate follow-up questions
        response_text = result.content
        follow_up_questions = [f"Can you elaborate on {keyword}?" for keyword in user_question.split()[:2]]

        return jsonify({
            "answer": response_text,
            "follow-up questions": follow_up_questions
        })
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
