from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain.vectorstores import Chroma


def get_conv_memory(self):
    """
    Builds conversation memory in vector store (Chromadb)
    """
    load_dotenv()
    store = Chroma.from_documents([], OpenAIEmbeddings(), persist_directory="../conv-db")
    retriever = store.as_retriever(search_kwargs=dict(k=1))
    return VectorStoreRetrieverMemory(retriever=retriever)
