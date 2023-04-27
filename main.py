import argparse
import os
from dotenv import load_dotenv
load_dotenv()

def init():
    # Init LLM
    pass



def main():
    # https://towardsdatascience.com/how-to-write-user-friendly-command-line-interfaces-in-python-cc3a6444af8e
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description="Target a IP ")
    parser.add_argument("-i", "--ip", type=str, help="URL of the target", required=True)
    parser.add_argument("-p", "--port", type=int, help="Optional port of the target")
    parser.add_argument("-k", "--knowledge", type=str, help="Optional known information about the target")
    parser.add_argument("-t", "--tools", type=str, nargs="+", help="Optional one or more target tools", 
                        choices=["tool1", "tool2", "tool3"])
    args = parser.parse_args()

    print(args.ip)
    print(args.port)
    print(args.knowledge)
    print(args.tools)

    apikey = os.getenv("OPENAI_API_KEY")


if __name__ == "__main__":
    main()
