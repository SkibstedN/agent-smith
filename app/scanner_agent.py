import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from bashtool import BashTool

load_dotenv()

# Initialize OpenAI client
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt_prefix = """
You are a penetration testing agent with permission to perform non-destructive security testing.
You have access to these tools ONLY: nmap, ping, curl.

You MUST follow these steps in EXACT order:
1. FIRST STEP: Use ping to resolve the target hostname to IP
   - Command: ping -c 1 <target>
   - Do not proceed until you have the IP address

2. SECOND STEP: After getting the IP, use nmap to scan for open ports
   - Command: nmap -sV <target>
   - Do not proceed until you have port scan results

3. FINAL STEP: Use curl to check any web services found
   - Command: curl -I http://<target>
   - Only proceed to this step after port scan

4. SECURITY SUGGESTIONS: Based on the findings, suggest next steps for security testing
   - Focus on the services and versions found
   - Suggest specific security checks
   - Keep suggestions brief and relevant

Important rules:
- You MUST start with ping, no exceptions
- Each command must be non-interactive (use appropriate flags)
- Use verbose flags when needed (e.g., curl -v, nmap -v)
- Do not skip any steps
- Do not combine steps

Return results in ReAct format:
Question: <current task>
Thought: <your reasoning>
Action: Terminal
Action Input: <exact command>
Observation: <command output>
Thought: <next step or conclusion>

Example sequence:
Question: What is the IP address of target?
Thought: I will use ping to resolve the hostname
Action: Terminal
Action Input: ping -c 1 target
Observation: <output>
Thought: Now I will scan for open ports
Action: Terminal
Action Input: nmap -sV target
Observation: <output>
Thought: I found web services, let me check them
Action: Terminal
Action Input: curl -I http://target
Observation: <output>
Thought: Done
Final Answer: • IP: <resolved IP>\n• Open ports: 80, 3306\n• Web server: Apache/2.4.7\n\nSuggested next steps for security testing:\n1. Check for common web vulnerabilities on port 80\n2. Test MySQL security on port 3306\n3. Look for outdated software versions

Remember: You MUST start with ping and follow the steps in order!
"""

def run_scanner_agent(args):
    """
    Runs a *very* limited ReAct agent that is only allowed to:
      • run nmap / ping / curl
      • collect port, service and banner information
      • end with a short bullet-point summary
    """
    # ────────────────────────────────────────────────
    load_dotenv()

    # 1) Large-language-model (OpenAI GPT-4)
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 2) The only tools the agent is allowed to use
    tools = [BashTool()]

    # 3) Simple memory (only for logging – no embeddings)
    memory = ConversationBufferMemory(return_messages=True)

    # 4) Build the ReAct agent
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        agent_kwargs={"prefix": prompt_prefix},
        verbose=True,
        handle_parsing_errors=True,   # Lets the agent fix small formatting errors
    )
    agent_executor.memory = memory

    # 5) Set the actual question (ReAct template expects key "input")
    target = f"{args.ip}:{args.port}" if args.port else args.ip
    question = f"Perform a complete security scan of target: {target}. You MUST start with ping to resolve the hostname, then scan for open ports, and finally check web services. After the scan, suggest relevant security testing steps based on the findings."
    print(question)

    # 6) Run – use .invoke so the input field is named "input"
    result = agent_executor.invoke({"input": question})

    # 7) Save the entire conversation if you want post-analysis
    with open("memory.txt", "w") as fh:
        fh.write(memory.json())

    return result




