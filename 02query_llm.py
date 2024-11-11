import argparse
# from dataclasses import dataclass
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
{context}
---
Answer the question based on the above context but do **not** include the context in your answer: {question}
"""


def process_query(query_text: str):
   
    # Prepare the DB.
    google_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    api_key=os.environ.get("GOOGLE_API_KEY"))
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=google_embeddings)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        return "Unable to find matching results."

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    # Show all infos about the response
    # response_text = model.predict(prompt)

    response = model.invoke(prompt)
    response_text = response.content
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return response_text
