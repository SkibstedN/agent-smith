import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from bashtool import BashTool

template = """Question: {question}

Answer: """


def init():
    # Init LLM
    pass


def main():
    load_dotenv()
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=1)
    tools = [BashTool()]
    agent = initialize_agent(tools, llm, agent='zero-shot-react-description', verbose=True)
    agent.run("Pentest my website: 127.0.0.1")
    


if __name__ == "__main__":
    main()

