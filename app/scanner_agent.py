import json
import re
from typing import List, Union

from dotenv import load_dotenv
from langchain.agents import AgentOutputParser, initialize_agent, AgentType
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from bashtool import BashTool


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
You must act as penetration tester agent who is allowed to test the security of the system. 
You goal is to scan the system for vulnerabilities.
You have access to nmap, nikto, ping etc. scanning tools from kali linux.
"ping" must be used with the following flags "-W 10 -c 3".
"""


# If any tool is not found, install it. If you can't install it, try another tool.


def run_scanner_agent(args):
    load_dotenv()
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")

    tools = [BashTool()]
    memory = ConversationBufferMemory()

    agent_executor = initialize_agent(tools=tools, llm=llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True, agent_kwargs={"prefix": prompt_prefix})

    agent_executor.memory = memory

    port = ":" + args.port if args.port is not None else ""

    prompt = """
    Do penetration testing and try to find exploits on the following site: '{ip}{port}' this is the complete hostname, there is no http:// or .com - the hostname is 'bwapp'
    You are only allowed to use the commands mentioned above.
    
    Knowledge: {knowledge}

    Stop when you have found vulnerabilities and when you are done summarize the vulnerabilities in bullet points.
    """.format(ip=args.ip, port=port, knowledge=args.knowledge)
    print(prompt)

    agent_executor.run(prompt)

    with open('memory.txt', 'w') as convert_file:
        if memory:
            convert_file.write(json.dumps(memory.json()))

    return memory
