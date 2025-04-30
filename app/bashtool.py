import shlex, subprocess
from langchain.tools import BaseTool

ALLOWED = {"nmap", "ping", "curl"}
TIMEOUT  = 120


class BashTool(BaseTool):
    name: str = "Terminal"
    description: str = "Kører nmap / ping / curl i et sandkasse-miljø og returnerer rå terminal-output."

    def _run(self, command: str) -> str:          # sync-kald (ReAct bruger denne)
        parts = shlex.split(command)

        if not parts or parts[0] not in ALLOWED:
            return f"Command '{parts[0] if parts else command}' not allowed."

        try:
            completed = subprocess.run(
                parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=TIMEOUT,
            )
            return completed.stdout.strip()
        except subprocess.TimeoutExpired:
            return f"Timeout after {TIMEOUT}s"

    async def _arun(self, command: str):          # async-variant ikke implementeret
        raise NotImplementedError("BashTool does not support async execution.")
