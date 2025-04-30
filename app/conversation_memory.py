from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
from langchain.memory import VectorStoreRetrieverMemory
from langchain.vectorstores import Chroma


def get_conv_memory(self):
    """
    Builds conversation memory in vector store (Chromadb)
    """
    load_dotenv()
    store = Chroma.from_documents([], hf, persist_directory="../conv-db")
