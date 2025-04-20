from datetime import datetime
from typing import Dict, Any, Tuple, List
import anthropic

def handle_interview_request(
    client: anthropic.Anthropic,
    sessions: Dict[str, Any],
    session_id: str = None,
    user_response: str = None,
    redacted_text: str = None,
    jd_text: str = None
) -> Tuple[Dict[str, Any], int]:
    """
    Handles interview requests, both starting new interviews and continuing existing ones.
    
    Args:
        client: Anthropic API client
        sessions: Dictionary of active interview sessions
        session_id: Existing session ID (None for new interviews)
        user_response: User's response in an ongoing interview
        redacted_text: Resume content (required for new interviews)
        jd_text: Job description content (required for new interviews)
        
    Returns:
        Tuple containing (response_data, status_code)
    """
    # CASE 1: Starting a new interview
    if session_id is None or session_id not in sessions:
        # Validate required fields for new interview
        if not redacted_text or not jd_text:
            return {"error": "Resume and job description are required for new interviews"}, 400
            
        # Generate a new session ID
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Setup context
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
        
        # Initialize session
        sessions[session_id] = {
            'messages': [],
            'started_at': datetime.now().isoformat(),
            'question_count': 0,
            'interview_complete': False,
            'system_prompt': system_prompt,
            'context': context
        }
        
        # Initial user message
        initial_message = "Hi, I'm here for a mock interview. Please introduce yourself and start the interview."
        
        # Store user's message
        sessions[session_id]['messages'].append({
            "role": "user", 
            "content": initial_message
        })
        
        # Get Claude's response
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            system=system_prompt,
            max_tokens=1000,
            context=context,
            messages=[{"role": "user", "content": initial_message}]
        )
        
        sessions[session_id]['thread_id'] = response.id
        
    # CASE 2: Continuing an existing interview
    else:
        # Get session data
        session_data = sessions[session_id]
        
        # Check if interview is already complete
        if session_data.get('interview_complete', False):
            return {
                "response": "This interview has already been completed. You can start a new one if you'd like.",
                "session_id": session_id,
                "interview_complete": True
            }, 200
        
        # Validate user response
        if not user_response:
            return {"error": "User response is required to continue the interview"}, 400
            
        # Add user response to messages
        session_data['messages'].append({
            "role": "user",
            "content": user_response
        })
        
        # Check if user wants to end the interview early
        end_interview_phrases = ["end interview", "stop interview", "exit", "quit", "let's finish", 
                                "finish interview", "terminate", "end session", "stop session"]
        
        force_end = any(phrase in user_response.lower() for phrase in end_interview_phrases)
        
        # Create a specific instruction for Claude based on the current state
        if force_end and session_data['question_count'] < 6:
            # User wants to end early - add a system note for Claude
            special_instruction = {
                "role": "user", 
                "content": "[System note: The candidate has requested to end the interview early. Please provide final feedback now.]"
            }
            session_data['messages'].append(special_instruction)
            session_data['interview_complete'] = True
        elif session_data['question_count'] >= 5:  # We've already asked 6 questions (0-indexed counting)
            # This will be the final response after the 6th question
            special_instruction = {
                "role": "user", 
                "content": user_response + "\n\n[System note: This is the response to the 6th question. Please provide final feedback now.]"
            }
            # Replace the last user message with our special instruction
            session_data['messages'][-1] = special_instruction
            session_data['interview_complete'] = True
        
        # Get Claude's response
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            system=session_data['system_prompt'],
            max_tokens=1000,
            context=session_data['context'],
            messages=session_data['messages'],
        )
    
    # Extract Claude's message
    claude_message = response.content[0].text
    
    # Store Claude's response in the session
    sessions[session_id]['messages'].append({
        "role": "assistant",
        "content": claude_message
    })
    
    # Handle question counting and completion status
    session_data = sessions[session_id]
    
    # Increment question count if this was a question (not feedback)
    if not session_data['interview_complete'] and "?" in claude_message:
        session_data['question_count'] += 1
        
        # Check if we've now reached 6 questions
        if session_data['question_count'] >= 6:
            session_data['interview_complete'] = True
    
    # Check if the interview is now complete based on Claude's response
    is_complete = session_data['interview_complete'] or any(
        phrase in claude_message.lower() for phrase in 
        ["overall impression", "thank you for participating", "final feedback", 
         "interview complete", "strengths and areas for improvement"]
    )
    
    if is_complete:
        session_data['interview_complete'] = True
    
    # Return response data
    return {
        "response": claude_message,
        "session_id": session_id,
        "question_count": session_data['question_count'],
        "interview_complete": session_data['interview_complete']
    }, 200

# def export_interview_data(sessions: Dict[str, Any], session_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Exports interview data for a given session.
    
    Args:
        sessions: Dictionary of active interview sessions
        session_id: Session ID to export
        
    Returns:
        Tuple containing (export_data, status_code)
    """
    # Check if session exists
    if session_id not in sessions:
        return {"error": "Session not found"}, 404
    
    # Get session data
    session_data = sessions[session_id]
    
    # Format messages for export
    formatted_messages = []
    for message in session_data['messages']:
        # Skip system notes
        if message['role'] == 'user' and '[System note:' in message['content']:
            continue
            
        role = "Interviewer" if message['role'] == "assistant" else "Candidate"
        formatted_messages.append({
            "speaker": role,
            "content": message['content']
        })
    
    # Prepare export data
    export_data = {
        "interview_id": session_id,
        "date": session_data['started_at'],
        "total_questions": session_data['question_count'],
        "transcript": formatted_messages
    }
    
    return export_data, 200