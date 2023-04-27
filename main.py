import argparse
import os
from dotenv import load_dotenv
load_dotenv()

def init():
    # Init LLM
    pass


# https://towardsdatascience.com/how-to-write-user-friendly-command-line-interfaces-in-python-cc3a6444af8e

def main():
    parser = argparse.ArgumentParser(description="Target a IP ")
    parser.add_argument("-t", "--target", type=str, help="URL of the target", required=True)
    parser.add_argument("-p", "--port", type=int, help="Optional port of the target")
    parser.add_argument("-i", "--info", type=str, help="Optional known information about the target")
    # parser.add_argument("-b", "--birth", type=str, help="Your birthday in YYYY-MM-DD format", required=True)
    # parser.add_argument("-m", "--manufacturer", type=str, nargs="+", help="The vaccine manufacturer", required=True, choices=[
    #         "pfizer","moderna","astrazeneca","janssen","sinovac"])
    # parser.add_argument("-d", "--date", type=str, nargs="+", help="The date of vaccination", required=True)
    args = parser.parse_args()

    print(args.target)
    print(args.port)
    print(args.info)
    
    apikey = os.getenv("OPENAI_API_KEY")
    
    print("This maybe works?")

if __name__ == "__main__":
    main()

