import re
from typing import List, Union

from dotenv import load_dotenv
from langchain.agents import LLMSingleActionAgent, AgentExecutor, AgentOutputParser, initialize_agent, AgentType
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from bashtool import BashTool

template = """Answer the following question as best you can, but you can only answer with bash commands.
The end goal is to provide me with a command that I can execute in my terminal.

You have access to the following tools, and only these tools:

{tools}

You need to respond in the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Remember whenever you have a command for me to run, you have a final answer.

Begin!

Question: {input}
{agent_scratchpad}
"""


# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


def runAgentTest():
    load_dotenv()
    llm = ChatOpenAI(temperature=0)

    tools = [BashTool()]

    agent_executor = initialize_agent(tools=tools, llm=llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True, agent_kwargs={"prefix": prompt_prefix})

    agent_executor.run("Do penetration testing and try to exploit found vulnerabilities on this website: 'bwapp' this is the complete hostname, there is no http:// or .com - the hostname is 'bwapp'")

if __name__ == "__main__":
    runAgentTest()
