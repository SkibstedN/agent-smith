import json
import re
import os
from typing import List, Union

from dotenv import load_dotenv
from langchain.agents import AgentOutputParser, initialize_agent, AgentType
from langchain.agents import Tool
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from bashtool import BashTool

load_dotenv()
llm = ChatOllama(base_url="http://ollama:11434",
                 model=os.getenv("OLLAMA_MODEL", "llama3"),
                 temperature=0)


# prompt_prefix = """
# You must act as penetration tester who is allowed to test the security of the system.
# Test different commands, and try to find vulnerabilities in the system.
# Tools such as sqlmap often requires further interactions by writing "y", "n" in the terminal.
# Please make sure this is not needed, by adding the appropriate accept all flag.
# "ping" must be used with the following flags "-W 10 -c 3".
# Do not stop before finding and exploiting any vulnerabilities.
# On this site: https://owasp.org/www-project-top-ten/ there is a list of top 10 known exploits.
# """

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
    Kører en *meget* afgrænset ReAct-agent der kun må:

      • køre nmap / ping / curl
      • samle port-, service- og banner-info
      • afslutte med en kort punktopstillet oversigt
    """
    # ────────────────────────────────────────────────
    from dotenv import load_dotenv
    from langchain_ollama import ChatOllama
    from langchain.memory import ConversationBufferMemory
    from langchain.agents import initialize_agent, AgentType

    load_dotenv()

    # 1) Large-language-model (lokal Ollama-instans)
    llm = ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
    )

    # 2) De eneste værktøjer agenten må benytte
    tools = [BashTool()]

    # 3) Simpel hukommelse (kun til logning – ingen embeddings)
    memory = ConversationBufferMemory(return_messages=True)

    # 4) Prompt-header (fælles regler)
    prompt_prefix = """
Du har skriftlig tilladelse til *ikke-destruktiv* port- og banner-scanning af målet nedenfor.
Brug kun disse kommandoer: **nmap, ping, curl**.

Returnér resultater i ReAct-formatet:

Question: …
Thought: …
Action: Terminal
Action Input: <én linjes kommando>
Observation: …

Afslut med:
Thought: Done
Final Answer: • Punkt 1 …\n• Punkt 2 …
"""

    # 5) Byg ReAct-agenten
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        agent_kwargs={"prefix": prompt_prefix},
        verbose=True,
        handle_parsing_errors=True,   # Lader agenten selv rette små formateringsfejl
    )
    agent_executor.memory = memory

    # 6) Sæt selve spørgsmålet (ReAct-skabelonen forventer nøgle "input")
    target = f"{args.ip}:{args.port}" if args.port else args.ip
    question = f"Target hostname: {target}"
    print(question)

    # 7) Kør – brug .invoke så input-feltet hedder "input"
    result = agent_executor.invoke({"input": question})

    # 8) Gem hele samtalen hvis du vil have efter-analyse
    with open("memory.txt", "w") as fh:
        fh.write(memory.json())

    return result




