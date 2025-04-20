from anthropic import Anthropic
import os
from typing import List, Dict, Any
import json

def conduct_mock_interview(resume_text: str, job_description: str, user_response: str = None, interview_state: Dict = None) -> Dict:
    """
    Conducts a mock interview session using the resume and job description as context.
    
    Args:
        resume_text: The redacted resume text
        job_description: The job description text
        user_response: The user's latest response in the interview (None for first interaction)
        interview_state: Current state of the interview including history and position
    
    Returns:
        Dict containing the interview response, updated state, and any other relevant information
    """
    # Initialize the client
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # If this is a new interview, initialize the state
    if interview_state is None:
        interview_state = {
            "messages": [],
            "question_count": 0,
            "current_stage": "introduction",
            "stages": ["introduction", "technical", "behavioral", "closing"]
        }

    # Create system prompt with context
    system_prompt = f"""
    You are an expert technical interviewer conducting a job interview. 
    
    # Context
    The candidate's resume: {resume_text}
    
    The job description: {job_description}
    
    # Interview Instructions
    - Your role is to act as the interviewer, asking questions relevant to the resume and job description
    - Ask one question at a time and wait for the user's response
    - Ask questions that assess both technical skills and behavioral fit
    - Focus on the candidate's qualifications in relation to the job requirements
    - Be professional but conversational
    - Provide constructive feedback only at the end when specifically asked
    - Do not simulate or generate the candidate's responses
    - Do not break character as the interviewer
    
    Current stage: {interview_state["current_stage"]}
    Questions asked so far: {interview_state["question_count"]}
    """
    
    # Build the conversation history for context
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for msg in interview_state["messages"]:
        messages.append(msg)
    
    # If this is the first interaction, generate initial interviewer greeting
    if user_response is None:
        interviewer_prompt = "Begin the interview with a professional introduction and your first question."
        messages.append({"role": "user", "content": interviewer_prompt})
    else:
        # Add the user's response to the messages
        messages.append({"role": "user", "content": user_response})
    
    # Call Claude with the complete context
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        system=system_prompt,
        messages=messages[1:]  # Exclude system prompt as it's passed separately
    )
    
    # Update interview state
    interview_state["messages"].append({"role": "user", "content": user_response if user_response else interviewer_prompt})
    interview_state["messages"].append({"role": "assistant", "content": response.content[0].text})
    
    # Update question count if this was an interviewer question
    if user_response is not None:
        interview_state["question_count"] += 1
    
    # Determine if we need to advance to the next stage
    if interview_state["question_count"] >= 3 and interview_state["current_stage"] != "closing":
        current_index = interview_state["stages"].index(interview_state["current_stage"])
        if current_index < len(interview_state["stages"]) - 1:
            interview_state["current_stage"] = interview_state["stages"][current_index + 1]
    
    return {
        "interviewer_response": response.content[0].text,
        "interview_state": interview_state,
        "success": True
    }
