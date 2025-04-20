# Add these routes to your FlaskIntegration.py

@app.route('/start_interview', methods=['POST'])
def start_interview():
    """Initialize a new mock interview session"""
    redacted_text = request.form.get('redacted_text', '')
    jd_text = request.form.get('job_description', '')
    
    if not redacted_text or not jd_text:
        return jsonify({'error': 'Resume text and job description are required'}), 400
    
    try:
        # Start new interview without user response (initial greeting)
        interview_response = conduct_mock_interview(redacted_text, jd_text)
        
        # Store interview state in session
        session['interview_state'] = interview_response['interview_state']
        session['resume_text'] = redacted_text
        session['job_description'] = jd_text
        
        return jsonify({
            'interviewer_message': interview_response['interviewer_response'],
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/continue_interview', methods=['POST'])
def continue_interview():
    """Continue an existing interview with user's response"""
    user_response = request.form.get('user_response', '')
    
    if not user_response:
        return jsonify({'error': 'User response is required'}), 400
    
    try:
        # Get interview state from session
        interview_state = session.get('interview_state')
        resume_text = session.get('resume_text')
        jd_text = session.get('job_description')
        
        if not interview_state or not resume_text or not jd_text:
            return jsonify({'error': 'Interview session not found or expired'}), 400
        
        # Continue interview with user response
        interview_response = conduct_mock_interview(
            resume_text, 
            jd_text,
            user_response, 
            interview_state
        )
        
        # Update interview state in session
        session['interview_state'] = interview_response['interview_state']
        
        return jsonify({
            'interviewer_message': interview_response['interviewer_response'],
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/end_interview', methods=['POST'])
def end_interview():
    """End the current interview session and get feedback"""
    try:
        # Clear session data
        interview_state = session.pop('interview_state', None)
        resume_text = session.pop('resume_text', None)
        jd_text = session.pop('job_description', None)
        
        if not interview_state or not resume_text or not jd_text:
            return jsonify({'error': 'No active interview session found'}), 400
        
        # Generate interview feedback
        from anthropic import Anthropic
        import os
        
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Extract conversation history
        messages = interview_state["messages"]
        
        feedback_prompt = f"""
        # Interview Feedback Request
        
        Resume: {resume_text}
        Job Description: {jd_text}
        
        Please provide constructive feedback on this mock interview, including:
        1. Overall assessment
        2. Communication strengths
        3. Areas for improvement
        4. Alignment with the job requirements
        """
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": "You are an expert interview coach providing constructive feedback."},
                *messages,
                {"role": "user", "content": feedback_prompt}
            ]
        )
        
        return jsonify({
            'feedback': response.content[0].text,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# Don't forget to add this import at the top of your file
from flask import session

# And add a secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
