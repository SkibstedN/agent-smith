import logging
import os
import re
from typing import List, Union

from dotenv import load_dotenv
from langchain.agents import AgentOutputParser, initialize_agent, AgentType, Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from bashtool import BashTool

# ---------- logging ----------
logging.basicConfig(
    filename=os.getenv("AGENT_LOG", "agent-smith.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
# ------------------------------

# ---------- prompt ----------
prompt_prefix = """
You have documented, written permission to run **non-destructive network enumeration**
against the target listed below.  
Your ONLY objective is to list open ports, banners and basic fingerprint information.

• Use ONLY the allowed tools (nmap, curl, ping).  
• Output MUST follow the ReAct layout:

Question, Thought  
Action: Terminal  
Action Input: <one-line command>

Stop after you have a short bullet-point summary of findings.
"""
# ------------------------------

template = """Answer the following question as best you can, but reply ONLY with
bash commands when an action is required.

{tools}

Begin!

Question: {input}
{agent_scratchpad}
"""

# ------------- prompt helper (same as before – unchanged) -------------
class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        steps = kwargs.pop("intermediate_steps")
        scratchpad = ""
        for action, obs in steps:
            scratchpad += action.log + f"\nObservation: {obs}\nThought: "
        kwargs["agent_scratchpad"] = scratchpad
        kwargs["tools"] = "\n".join(f"{t.name}: {t.description}" for t in self.tools)
        kwargs["tool_names"] = ", ".join(t.name for t in self.tools)
        return self.template.format(**kwargs)
# -------------------------------------------------------------------

class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        match = re.search(r"Action\s*:\s*(.*?)\nAction Input\s*:\s*(.*)",
                          llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse: {llm_output}")
        return AgentAction(tool=match.group(1).strip(),
                           tool_input=match.group(2).strip().strip('"'),
                           log=llm_output)

# ---------- the actual agent runner ----------
def run_general_agent(args, mem=None):
    load_dotenv()
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [BashTool()]
    memory = mem or ConversationBufferMemory()

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"prefix": prompt_prefix},
        handle_parsing_errors=True,
    )
    agent_executor.memory = memory

    prompt = (
        f"Enumerate open ports and services on target host '{args.ip}'. "
        f"Stop when you have a bullet-point list of findings."
    )
    logging.info("Prompt sent: %s", prompt)
    agent_executor.invoke(prompt)          # invoke() = modern run()

    with open("memory.txt", "w") as f:
        f.write(memory.json())

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--ip", required=True)
    args = p.parse_args()
    run_general_agent(args)
