from langchain.tools import BaseTool
from langchain.utilities import BashProcess


class BashTool(BaseTool):
    name = "Terminal"
    description = "Executes commands in a terminal. Input should be valid commands, and the output will be any output from running that command."

    def _run(self, command: str) -> str:
        """Run commands and return final output."""
        # By default, the bash command will be executed in a new subprocess each time. 
        # To retain a persistent bash session, we can use the persistent=True arg.
        bash = BashProcess(strip_newlines=True, return_err_output=True)
        return bash.run(command)

    async def _arun(self, command: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("BashTool does not support async")
