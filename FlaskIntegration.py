from flask import Flask, render_template, session, request, send_file, jsonify, make_response
from flask_session import Session

import os
import io
import tempfile
from werkzeug.utils import secure_filename
import spacy
import phonenumbers
import pyap
import re
from typing import Dict, List, Tuple, Optional, BinaryIO, Union
from PyPDF2 import PdfReader
from redactr import redact_pdf
from claude_utils import get_full_resume_review, clean_claude_response
from mock_interview_integration import conduct_mock_interview
from anthropic import Anthropic

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.local")


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config["SESSION_TYPE"] = "filesystem"  # Store sessions on server filesystem

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

Session(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdf_file']
    jd_text = request.form["jd_text"]
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if len(jd_text) == 0:
        return jsonify({'error': 'No job description'}), 400
    
    # if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'pdf':
        # Process the PDF
    redacted_text = redact_pdf(file)
    
    # Create a response with the redacted text and statistics
    response = {
        'redacted_text': redacted_text,
        'job_description' : jd_text,
        'auto_switch_tab': True  # Flag to trigger automatic tab switch
    }
    
    return jsonify(response)
    
    # return jsonify({'error': 'File must be a PDF'}), 400


@app.route('/download', methods=['POST'])
def download_redacted():
    text = request.form.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    temp_file.write(text.encode('utf-8'))
    temp_file.close()
    
    response = make_response(send_file(temp_file.name, as_attachment=True, 
                                      download_name='redacted_text.txt'))
    
    # Clean up the file after sending
    @response.call_on_close
    def cleanup():
        os.remove(temp_file.name)
    
    return response


@app.route('/process_with_claude', methods=['POST'])
def process_with_claude():
    redacted_text = request.form.get('redacted_text', '')
    jd_text = request.form.get('job_description', '')

    if not redacted_text:
        return jsonify({'error': 'No text provided for processing'}), 400
    
    # Call the Claude wrapper function with the redacted text
    try:
        claude_response = call_claude_wrapper(redacted_text, jd_text)
        return jsonify({'claude_response': claude_response, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

def call_claude_wrapper(redacted_text, jd_text):
    """
    Function to process redacted text with Claude API
    This is a placeholder - implement the actual Claude API call here
    """
    raw_output = get_full_resume_review(redacted_text, jd_text)
    return clean_claude_response(raw_output)

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
        print("clearing session data")
        interview_state = session.pop('interview_state', None)
        resume_text = session.pop('resume_text', None)
        jd_text = session.pop('job_description', None)
        
        if not interview_state or not resume_text or not jd_text:
            return jsonify({'error': 'No active interview session found'}), 400
        
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Extract conversation history
        print("extracting conversation")
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
            model="claude-3-7-sonnet-20250219",
            max_tokens=2048,
            messages=[
                {"role": "assistant", "content": "You are an expert interview coach providing constructive feedback."},
                *messages,
                {"role": "user", "content": feedback_prompt}
            ]
        )
        
        return jsonify({
            'feedback': clean_claude_response(response.content[0].text),
            'success': True
        })
    except Exception as e:
        print(e)
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True)