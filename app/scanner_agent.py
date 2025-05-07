import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory

from bashtool import BashTool

load_dotenv()
llm = ChatOllama(base_url="http://ollama:11434",
                 model=os.getenv("OLLAMA_MODEL", "llama3"),
                 temperature=0)

prompt_prefix = """
You are a ReAct agent. Never return JSON. Use the exact
ReAct format described below.

You have written permission to enumerate open ports and banners
on the host below. Use only: nmap, ping, curl.

Respond **exactly** in ReAct style, e.g.

Question: <text>
Thought: <your reasoning>
Action: Terminal
Action Input: nmap -sV bwapp
Observation: <command output>
Thought: ...
Final Answer: <bullet-list of findings>

Do **not** use JSON, markdown or code fences.
"""

# If any tool is not found, install it. If you can't install it, try another tool.

def run_scanner_agent(args):
    """
    Runs a *very* limited ReAct agent that is only allowed to:

      • run nmap / ping / curl
      • collect port, service and banner information
      • end with a short bullet-point summary
    """
    # ────────────────────────────────────────────────
    load_dotenv()

    # 1) Large-language-model (local Ollama instance)
    llm = ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
    )

    # 2) The only tools the agent is allowed to use
    tools = [BashTool()]

    # 3) Simple memory (only for logging – no embeddings)
    memory = ConversationBufferMemory(return_messages=True)

    # 4) Prompt-header (common rules)
    prompt_prefix = """
You have written permission for *non-destructive* port and banner scanning of the target below.
Only use these commands: **nmap, ping, curl**.

Return results in ReAct format:

Question: …
Thought: …
Action: Terminal
Action Input: <one-line command>
Observation: …

End with:
Thought: Done
Final Answer: • Point 1 …\n• Point 2 …
"""

    # 5) Build the ReAct agent
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        agent_kwargs={"prefix": prompt_prefix},
        verbose=True,
        handle_parsing_errors=True,   # Lets the agent fix small formatting errors
    )
    agent_executor.memory = memory

    # 6) Set the actual question (ReAct template expects key "input")
    target = f"{args.ip}:{args.port}" if args.port else args.ip
    question = f"Target hostname: {target}"
    print(question)

    # 7) Run – use .invoke so the input field is named "input"
    result = agent_executor.invoke({"input": question})

    # 8) Save the entire conversation if you want post-analysis
    with open("memory.txt", "w") as fh:
        fh.write(memory.json())

    return result




