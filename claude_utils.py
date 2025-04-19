# This is a wrapper file that wraps all the Claude API logic 
import anthropic
import os
from dotenv import load_dotenv

# loading the .env file where your key is stored
load_dotenv()

# setting up the Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# helper function to send prompt and get a response
def call_claude(prompt, system_msg="You are a resume reviewer."):
    try:
        # claude message call (you can change model, temp, etc.)
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            temperature=0.7,
            system=system_msg,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # return just the useful part
        return response.content 
    except Exception as e:
        print(f"[Claude error] {e}")
        return "Claude is not responding right now. Please try again."
