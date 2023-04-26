# agent-smith
Spawn endless swarms of GPT4 agents using LangChain to scan for vulnerabilities in your software!

## White-hat hacker agents styret af GPT4 (3.5)
***Projekt idé (Originalt af Morten)***

> Brug GPT4 til at automatisere en 'whitehacking' bot. GPT4 udvides til at kunne eksekvere pen-testing. Dvs. at vi bruger GPT4 API'et til at definere kommandoer som vi eksekverer i en terminal, og responset giver vi så til GPT4, som så giver en ny kommando osv. Vi kunne lade os inspirere af https://github.com/Significant-Gravitas/Auto-GPT. Det kunne også være en mulighed at bruge https://js.langchain.com/docs/.

---

Først og fremmest skal vi lege med OpenAI's GPT API for at se hvad det kan!

Gode udfordringer vi står overfor:

- (CLI tool) Hvordan skal værktæjet tage imod target (api url, website etc.) og goal (målet med undersøgelse/forsøg på sikekrhedsbrud)?
- (Prompts) Hvilke forskellige prompts (pre-prompts) skal vi bruge?
  - Forskellige agents skal kunne forskellige ting (evt. samarbejde?). Det kunne f.eks. agents til hver af OWASPs top 10 Web Application Security Risks [OWAPS Top10](https://owasp.org/www-project-top-ten/)
  - F.eks.  Broken Access Control, sql-injection, Misconfiguration, Vuln. and outdated components etc. Port Scanning..
- (Command Executor) Hvad gør vi med long-running commands (nmap uden specifik port)?
  - Kan vi køre commands sikkert uden af flå vores computer fra hinanden?
- Skal skal prøve at bruge LangChains "Agent" til at spawne forskellige GPT agents der kan hjælpe hinanden eller samarbejde om et target. (Tænk: spawn 100 agents der pinger et api med forskellige tools)
- Hvordan håndtere vi "known" viden som f.eks. CVE register?
- Skal vi gøre det i Python eller JS?
  - [LangChain JS vs. Python Integrations](https://langchain.com/integrations.html)
  - [LangChain JS vs. Python Features](https://langchain.com/features.html)

Illustration af ide:

```mermaid
flowchart TD
    subgraph White-hat hacker
    direction TB
    subgraph Open AI API
    G[GPT4]
    end

    subgraph LangChain
    direction RL
    B[Agent A]
    E((Promts))
    E --> |3. Relevant Promt| B
    B --> |2. Goals A| E
    F[CLI tool]   
    F --> |1. Enter Goal and Target| B
    B --> |?. search| C[(Indexes:\nCVE register)]
    C --> |?. Known vuln.| B
    D[Command Executor]
    B --> |6. Execute Command A| D
    D --> |7. Command Output A| B
    end

    B -->|4. Task A| G
    G -->|5. Command A| B
    end
```


