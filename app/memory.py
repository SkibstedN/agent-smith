import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, TextLoader

class CveMemory:

    def __init__(self):
        load_dotenv()
        self.persist_directory = "../db"
        self.embeddings = OpenAIEmbeddings()

    def build_memory(self):
        """
        Builds CVE memory in vector store (Chromadb)
        """
        load_dotenv()

        cve_path = os.path.dirname(__file__) + '/../cves'
        print(cve_path)

        loader = DirectoryLoader(cve_path, glob="**/*.json", show_progress=True, loader_cls=TextLoader)

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(loader.load())

        vectordb = Chroma.from_documents(docs, self.embeddings, persist_directory=self.persist_directory)
        vectordb.persist()

    def query_memory(self, query: str):
        """
        Du a similarity search in CVE memory vector store
        @param query: query str
        @return: page_content (str)
        """
        vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        docs = vectordb.similarity_search(query, k=1)
        return docs[0].page_content
