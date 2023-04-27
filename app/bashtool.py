from langchain.tools import BaseTool
from langchain.utilities import BashProcess

class BashTool(BaseTool):
    name = "Bash"
    description = "useful for when you need to run bash commands"

    def _run(self, command: str) -> str:
        """Run commands and return final output."""
        # By default, the bash command will be executed in a new subprocess each time. 
        # To retain a persistent bash session, we can use the persistent=True arg.
        bash = BashProcess(strip_newlines=True) 
        return bash.run(command)

    async def _arun(self, command: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("BashTool does not support async")



