from flask import Flask, render_template, request, send_file, jsonify, make_response
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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdf_file']
    jd_text = request.form["jd_text"]
    #print(jd_text)
    
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
    print(jd_text)
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
    # return get_full_resume_review(redacted_text, jd_text)

    # Implementation would go here - e.g., API call to Claude
    #return f"Claude's analysis of the redacted resume would appear here."


if __name__ == '__main__':
    app.run(debug=True)