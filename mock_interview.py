import os
import json
import anthropic
from typing import Optional, Dict, Any, List

def conduct_mock_interview(
    api_key: str,
    resume_path: str,
    job_description_path: str,
    model: str = "claude-3-7-sonnet-20250219"
) -> None:
    """
    Conducts a mock interview using Claude API with resume and job description as context.
    
    Args:
        api_key: Your Anthropic API key
        resume_path: Path to the resume file (PDF or text)
        job_description_path: Path to the job description file (PDF or text)
        model: Claude model to use (defaults to Claude 3.7 Sonnet)
    """
    # Initialize the client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load resume and job description
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_content = f.read()
    
    with open(job_description_path, 'r', encoding='utf-8') as f:
        job_description_content = f.read()
    
    # Setup context using Model Context Protocol
    context = [
        {
            "id": "resume",
            "content": resume_content,
            "description": "The candidate's resume"
        },
        {
            "id": "job_description",
            "content": job_description_content,
            "description": "The job description for the position being interviewed for"
        }
    ]
    
    # Initial system prompt for Claude to act as an interviewer
    system_prompt = """
    You are an experienced hiring manager conducting a job interview. You have access to the candidate's resume and the job description via the Model Context Protocol. Your task is to:

    1. Begin by introducing yourself and explaining the interview process
    2. Ask 5-10 relevant interview questions based on the job description and resume
    3. Make the questions conversational and tailored to the position requirements
    4. Listen to each response before asking the next question
    5. After all questions have been answered, provide constructive feedback highlighting:
       - The candidate's strongest points
       - Areas where the candidate could improve
       - Overall impression and fit for the role

    Keep track of the number of questions asked. When you reach the final question, indicate that it's the last one before feedback.
    Be professional yet conversational throughout the interview.
    """
    
    # Start the conversation with Claude
    messages = [
        {
            "role": "user", 
            "content": "I'm ready to start my mock interview. Please introduce yourself and begin the interview based on my resume and the job description."
        }
    ]
    
    # Main interview loop
    print("\n--- MOCK INTERVIEW SESSION STARTING ---\n")
    try:
        while True:
            # Get Claude's response
            response = client.messages.create(
                model=model,
                system=system_prompt,
                messages=messages,
                context=context,
                max_tokens=2000
            )
            
            # Display Claude's message (interview question or feedback)
            claude_message = response.content[0].text
            print(f"\nInterviewer: {claude_message}")
            
            # Check if the interview is complete (feedback has been provided)
            if "overall impression" in claude_message.lower() or "thank you for participating" in claude_message.lower():
                print("\n--- INTERVIEW COMPLETE ---\n")
                break
            
            # Get user's response
            user_response = input("\nYour answer: ")
            
            # Add messages to the conversation history
            messages.append({"role": "assistant", "content": claude_message})
            messages.append({"role": "user", "content": user_response})
            
    except KeyboardInterrupt:
        print("\n\nInterview terminated by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")

if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = input("Please enter your Anthropic API key: ")
    
    resume_path = input("Path to your resume file: ")
    job_description_path = input("Path to the job description file: ")
    
    conduct_mock_interview(api_key, resume_path, job_description_path)