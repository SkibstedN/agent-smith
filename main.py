import os
from dotenv import load_dotenv
load_dotenv()

def init():
    # Init LLM
    pass


def main():
    apikey = os.getenv("OPENAI_API_KEY")
    
    print("This maybe works?")

if __name__ == "__main__":
    main()

