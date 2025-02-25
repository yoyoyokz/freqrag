# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# import nltk
# nltk.data.path.append('/home/aka/nltk_data')
# from langchain.tokenizers import SpacyTokenizer
# import os
# from langchain.embeddings import OpenAIEmbeddings
# from langchain_google_vertexai import VertexAIEmbeddings
# from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
# openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "chroma"
DATA_PATH = "/data/documentation"

# Initialize the a specific Embeddings Model version
# embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# Use your environment variable for authentication
google_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    api_key=os.environ.get("GOOGLE_API_KEY")  # or any other required params
)


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader("./data/documentation", glob="*.md")
    documents = loader.load()
    
    # Debugging output
    print(f"Loaded documents: {documents}")
    if not documents:
        print("No documents found.")
    
    return documents


def split_text(documents: list[Document]):
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    # print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # document = chunks[10]
    # print(document.page_content)
    # print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    print(chunks[10])
    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, 
        embedding=google_embeddings,  # Use GoogleGenerativeAIEmbeddings
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()
