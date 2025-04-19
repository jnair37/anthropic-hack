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
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'pdf':
        # Process the PDF
        redacted_text, replacements = redact_pdf(file)
        
        # Count by type
        type_counts = {}
        for replacement in replacements.values():
            type_name = replacement.split('_')[0][1:]  # Extract type name from [TYPE_X]
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Create a response with the redacted text and statistics
        response = {
            'redacted_text': redacted_text,
            'replacements_count': len(replacements),
            'type_counts': type_counts
        }
        
        return jsonify(response)
    
    return jsonify({'error': 'File must be a PDF'}), 400


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


if __name__ == '__main__':
    app.run(debug=True)