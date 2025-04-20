# This is a wrapper file that wraps all the Claude API logic 
import anthropic
import os
from dotenv import load_dotenv
from prompts import full_review_prompt
import re
import markdown2

# loading the .env file where your key is stored
load_dotenv(dotenv_path=".env.local")

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
        print(response)
        return ''.join([block.text for block in response.content if block.type == "text"])
    except Exception as e:
        print(f"[Claude error] {e}")
        return "Claude is not responding right now. Please try again."
    
    
def get_full_resume_review(resume_text, jd_text):
    prompt = full_review_prompt(resume_text, jd_text)
    return call_claude(prompt)


def clean_claude_response(text: str) -> str:
    """Convert Claude Markdown-style response to HTML for display."""
    # Remove any <tags> like <job_fit> and <analysis> that Claude uses
    cleaned = re.sub(r"</?[\w_]+>", "", text)
    # Convert Markdown to HTML
    return markdown2.markdown(cleaned)