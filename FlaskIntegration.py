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


# HTML Templates
@app.route('/templates/index.html')
def serve_index_template():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Redaction Tool</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .container { max-width: 800px; margin-top: 30px; }
            #redacted-text { height: 400px; }
            .hidden { display: none; }
            .loading { text-align: center; padding: 20px; }
            .spinner-border { width: 3rem; height: 3rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Resume Redaction Tool</h1>
            
            <div class="card mb-4">
                <div class="card-header">
                    <ul class="nav nav-tabs card-header-tabs" id="myTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="upload-tab" data-bs-toggle="tab" data-bs-target="#upload" type="button" role="tab">Upload Resume</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="results-tab" data-bs-toggle="tab" data-bs-target="#results" type="button" role="tab">Results</button>
                        </li>
                    </ul>
                </div>
                <div class="card-body">
                    <div class="tab-content" id="myTabContent">
                        <div class="tab-pane fade show active" id="upload" role="tabpanel">
                            <p class="card-text">Upload a resume PDF to redact personal information:</p>
                            <form id="upload-form" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <input class="form-control" type="file" id="pdf-file" name="pdf_file" accept=".pdf">
                                </div>
                                <button type="submit" class="btn btn-primary">Process Resume</button>
                            </form>
                            
                            <div id="loading" class="loading hidden">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2">Processing PDF...</p>
                            </div>
                        </div>
                        
                        <div class="tab-pane fade" id="results" role="tabpanel">
                            <div id="results-container">
                                <div id="stats-container" class="mb-3">
                                    <h4>Redaction Statistics</h4>
                                    <div id="stats-content"></div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="redacted-text" class="form-label">Redacted Text</label>
                                    <textarea class="form-control" id="redacted-text" readonly></textarea>
                                </div>
                                
                                <button id="download-btn" class="btn btn-success">Download Redacted Text</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const uploadForm = document.getElementById('upload-form');
                const pdfFileInput = document.getElementById('pdf-file');
                const loadingDiv = document.getElementById('loading');
                const resultsTab = document.getElementById('results-tab');
                const redactedTextArea = document.getElementById('redacted-text');
                const statsContent = document.getElementById('stats-content');
                const downloadBtn = document.getElementById('download-btn');
                
                uploadForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData();
                    formData.append('pdf_file', pdfFileInput.files[0]);
                    
                    // Show loading spinner
                    loadingDiv.classList.remove('hidden');
                    
                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(data.error);
                            return;
                        }
                        
                        // Hide loading spinner
                        loadingDiv.classList.add('hidden');
                        
                        // Populate results
                        redactedTextArea.value = data.redacted_text;
                        
                        // Populate statistics
                        let statsHtml = `<p>Total items redacted: ${data.replacements_count}</p><ul>`;
                        for (const [type, count] of Object.entries(data.type_counts)) {
                            statsHtml += `<li>${type}: ${count} items</li>`;
                        }
                        statsHtml += '</ul>';
                        statsContent.innerHTML = statsHtml;
                        
                        // Switch to results tab
                        resultsTab.click();
                    })
                    .catch(error => {
                        loadingDiv.classList.add('hidden');
                        alert('An error occurred: ' + error);
                    });
                });
                
                downloadBtn.addEventListener('click', function() {
                    const formData = new FormData();
                    formData.append('text', redactedTextArea.value);
                    
                    fetch('/download', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.blob())
                    .then(blob => {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = 'redacted_text.txt';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                    })
                    .catch(error => alert('Download failed: ' + error));
                });
            });
        </script>
    </body>
    </html>
    '''
    return html


if __name__ == '__main__':
    app.run(debug=True)