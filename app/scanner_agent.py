import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from nvd_api import NVDApi
from typing import Dict, List

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
   - Include relevant CVE information for outdated software

Important rules:
- You MUST start with ping, no exceptions
- Each command must be non-interactive (use appropriate flags)
- Use verbose flags when needed (e.g., curl -v, nmap -v)
- Do not skip any steps
- Do not combine steps
- Always include CVE information for identified software versions

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
Final Answer: • IP: <resolved IP>
• Open ports: 80, 3306
• Web server: Apache/2.4.7
• CVE Information:
  - CVE-2021-44790: Apache 2.4.7 vulnerability (CVSS: 7.5)
  - CVE-2021-21703: PHP 5.5.9 vulnerability (CVSS: 9.8)

Suggested next steps for security testing:
1. Check for common web vulnerabilities on port 80
2. Test MySQL security on port 3306
3. Look for outdated software versions
4. Address critical CVEs identified above

Remember: You MUST start with ping and follow the steps in order!
"""

def run_scanner_agent(args):
    """
    Runs a security scan agent that:
    1. Uses ping, nmap, and curl for initial scanning
    2. Enhances findings with CVE data from NVD
    3. Provides detailed pentest guidance
    """
    # Initialize NVD API
    nvd_api = NVDApi()
    
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
        verbose=False,  # Set to False to suppress chain output
        handle_parsing_errors=True,
    )
    agent_executor.memory = memory

    # 5) Set the actual question
    target = f"{args.ip}:{args.port}" if args.port else args.ip
    question = f"Perform a complete security scan of target: {target}. You MUST start with ping to resolve the hostname, then scan for open ports, and finally check web services. After the scan, suggest relevant security testing steps based on the findings. Include CVE information for any identified software versions."

    # 6) Run the initial scan
    scan_result = agent_executor.invoke({"input": question})

    # 7) Only enhance with CVE data if not already present
    if isinstance(scan_result, dict) and "output" in scan_result:
        output = scan_result["output"]
        if "CVE Information" not in output and "CVE-" not in output:
            # Extract service information from scan results
            services = []
            for line in output.split("\n"):
                # Look for service version patterns like "Apache/2.4.7" or "PHP/5.5.9"
                if "/" in line:
                    parts = line.split("/")
                    if len(parts) >= 2:
                        service_name = parts[0].strip()
                        version = parts[1].strip()
                        # Clean up version (remove any extra info after space)
                        version = version.split()[0]
                        services.append({
                            "name": service_name,
                            "version": version
                        })

            # Search for CVEs based on services
            cve_info = []
            for service in services:
                try:
                    # Search for CVEs using the actual service name and version
                    cve_data = nvd_api.search_cves(f"{service['name']} {service['version']}")
                    if cve_data and cve_data.get("totalResults", 0) > 0:
                        cve = cve_data["vulnerabilities"][0]
                        report = nvd_api.format_vulnerability_report(cve)
                        cve_info.append({
                            "service": f"{service['name']} {service['version']}",
                            "cve_id": report["cve_id"],
                            "description": report["description"],
                            "cvss_score": report["cvss_score"],
                            "severity": report["severity"],
                            "references": report["references"],
                            "recommendations": report["recommendations"],
                            "testing_steps": report.get("testing_steps", [])
                        })
                except Exception as e:
                    print(f"Warning: Error processing CVE data for {service['name']} {service['version']}: {str(e)}")
                    continue

            # Add CVE information to the final answer
            if cve_info:
                final_answer = output
                if "CVE Information" in final_answer:
                    # Replace the CVE section with enhanced information
                    parts = final_answer.split("CVE Information")
                    if len(parts) > 1:
                        final_answer = parts[0] + "\n### Vulnerabilities and CVEs\n\n"
                        for cve in cve_info:
                            final_answer += f"#### {cve['service']}\n"
                            final_answer += f"- {cve['cve_id']}: {cve['description']}\n"
                            final_answer += f"  - CVSS Score: {cve['cvss_score']} ({cve['severity']})\n"
                            final_answer += "  - Testing Steps:\n"
                            for step in cve['testing_steps']:
                                final_answer += f"    - {step}\n"
                            final_answer += "  - Recommendations:\n"
                            for rec in cve['recommendations']:
                                final_answer += f"    - {rec}\n"
                        final_answer += parts[1].split("\n\n", 1)[1] if "\n\n" in parts[1] else ""
                scan_result["output"] = final_answer

    # 8) Save the entire conversation
    with open("memory.txt", "w") as fh:
        fh.write(memory.json())

    # Return only the final answer without any chain output
    if isinstance(scan_result, dict) and "output" in scan_result:
        output = scan_result["output"]
        # Extract just the final answer part
        if "Final Answer:" in output:
            output = output.split("Final Answer:")[-1].strip()
        # Remove any chain output
        if "> Finished chain." in output:
            output = output.split("> Finished chain.")[0].strip()
        # Remove References section
        if "References:" in output:
            output = output.split("References:")[0].strip()
        return output
    return str(scan_result)




