import argparse

from agent import run_general_agent
from scanner_agent import run_scanner_agent


def build_prompt(args) -> str:
    output = f"Target: {args.ip}"
    if args.port is not None:
        output += f", Port: {args.port}"
    if args.knowledge is not None:
        output += f", Knowledge: {args.knowledge}"
    if args.tools is not None:
        output += f", Tools: {args.tools}"

    return output


def main():
    # https://towardsdatascience.com/how-to-write-user-friendly-command-line-interfaces-in-python-cc3a6444af8e
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description="Target an IP ")
    parser.add_argument("-i", "--ip", type=str, help="URL of the target", required=True)
    parser.add_argument("-p", "--port", type=int, help="Optional port of the target")
    parser.add_argument("-k", "--knowledge", type=str, help="Optional known information about the target")
    parser.add_argument("-g", "--goal", type=str, help="Enter goal for the agent ('scan')")
    args = parser.parse_args()

    if args.goal == "scan":
        result = run_scanner_agent(args)
        print(result)
    else:
        run_general_agent(args)


if __name__ == "__main__":
    main()
