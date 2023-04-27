import argparse
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

def build_prompt(args) -> str:
    start_prompt = f"Target: {args.ip}"
    if args.port is not None:
        output += f", Port: {args.port}"
    if args.knowledge is not None:
        output += f", Knowledge: {args.knowledge}"
    if args.tools is not None:
        output += f", Tools: {args.tools}"
    
    return start_prompt


def main():
    # https://towardsdatascience.com/how-to-write-user-friendly-command-line-interfaces-in-python-cc3a6444af8e
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description="Target a IP ")
    parser.add_argument("-i", "--ip", type=str, help="URL of the target", required=True)
    parser.add_argument("-p", "--port", type=int, help="Optional port of the target")
    parser.add_argument("-k", "--knowledge", type=str, help="Optional known information about the target")
    parser.add_argument("-t", "--tools", type=str, nargs="+", help="Optional one or more target tools", 
                        choices=["tool1", "tool2", "tool3"])
    args = parser.parse_args()

    print(args.ip)
    print(args.port)
    print(args.knowledge)
    print(args.tools)

    load_dotenv()
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=1)
    tools = [BashTool()]
    agent = initialize_agent(tools, llm, agent='zero-shot-react-description', verbose=True)
    
    prompt = build_prompt(args)
    agent.run(prompt)


if __name__ == "__main__":
    main()
