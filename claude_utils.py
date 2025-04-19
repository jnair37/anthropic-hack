# This is a wrapper file that wraps all the Claude API logic 
import anthropic
import os
from dotenv import load_dotenv
from prompts import feedback_prompt

# loading the .env file where your key is stored
load_dotenv()

# setting up the Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# helper function to send prompt and get a response
def call_claude(prompt, system_msg="You are a resume reviewer. Also, we know the resume is redacted so ignore that."):
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
        return ''.join([block.text for block in response.content if block.type == "text"])
    except Exception as e:
        print(f"[Claude error] {e}")
        return "Claude is not responding right now. Please try again."
    
    
def get_resume_feedback(resume_text):
    prompt = feedback_prompt(resume_text)
    return call_claude(prompt)
