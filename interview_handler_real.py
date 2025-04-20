from datetime import datetime
from typing import Dict, Any, Tuple, List
import anthropic

@app.route('/interview', methods=['POST'])
def interview():
    redacted_text = request.form.get('redacted_text', '')
    jd_text = request.form.get('job_description', '')

    # Generate a session ID
    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Initialize session
    sessions[session_id] = {
        'messages': [],
        'started_at': datetime.now().isoformat(),
        'question_count': 0,
        'interview_complete': False
    }
    
    # Setup context using Model Context Protocol
    context = [
        {
            "id": "resume",
            "content": redacted_text,
            "description": "The candidate's resume with personal information redacted"
        },
        {
            "id": "job_description",
            "content": jd_text,
            "description": "The job description for the position being interviewed for"
        }
    ]
    
    # Save context to session for future API calls
    sessions[session_id]['context'] = context
    
    # Create system prompt for the interview
    system_prompt = """
    You are an experienced hiring manager conducting a job interview. You have access to the candidate's resume and the job description via the Model Context Protocol. Your task is to:

    1. Begin by introducing yourself and explaining the interview process
    2. Ask relevant interview questions based on the job description and resume
    3. Make the questions conversational and tailored to the position requirements
    4. After each candidate response, provide a follow-up question until you've asked a total of 6 questions
    5. Keep track of the number of questions you've asked
    6. After the 6th question and response, provide constructive feedback highlighting:
       - The candidate's strongest points
       - Areas where the candidate could improve
       - Overall impression and fit for the role

    If at any point the candidate says something like "end interview", "stop interview", "exit", "quit", "let's finish", or similar phrases indicating they want to end the session, you should skip to providing final feedback.

    Always number your questions clearly so both you and the candidate can keep track of progress.
    Be professional yet conversational throughout the interview.
    """
    
    # Save system prompt to session for future API calls
    sessions[session_id]['system_prompt'] = system_prompt
    
    # Set the first message from Claude
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        system=system_prompt,
        max_tokens=1000,
        context=context,
        messages=[
            {"role": "user", "content": "Hi, I'm here for a mock interview. Please introduce yourself and start the interview."}
        ]
    )
    
    # Store the conversation
    sessions[session_id]['messages'].append({
        "role": "user", 
        "content": "Hi, I'm here for a mock interview. Please introduce yourself and start the interview."
    })
    sessions[session_id]['messages'].append({
        "role": "assistant", 
        "content": response.content[0].text
    })
    
    # Store session ID in a cookie
    resp = jsonify({"response": response.content[0].text, "session_id": session_id})
    return resp