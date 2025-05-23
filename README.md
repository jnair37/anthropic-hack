# PrivaCV
### By Jade Nair, Karina Chung, and Zainab Adamji

![Alt text](img/Mock_interview.png)

PrivaCV is a webapp that uses AI to help candidates receive resume feedback and take mock interviews, while avoiding the risks of sending personal information to a large language model.

## Overview

Our goal is to help make resume feedback and interview preparation more accessible while providing a convenient way to privatize personal information. Therefore, PrivaCV is designed to help job seekers improve their resume and interview skills through a privacy-first approach. The tool allows users to:

1. Upload their resume PDF for automatic redaction of personal identifiers
2. Review and edit the redacted text before analysis
3. Receive detailed AI feedback on resume quality, strengths, and improvement areas
4. Practice with AI-powered mock interviews based on the resume and job description
5. Get interview feedback and performance evaluation

## Features

### 📄 Resume Redaction
- Automatically removes personal identifiers from your resume
- Allows manual review and editing of redacted content
- Download redacted text as a standalone file

### 🔍 Claude AI Analysis
- Detailed analysis of resume content, structure, and format
- Strengths and weaknesses assessment
- Targeted improvement recommendations
- Job-specific feedback when a job description is provided

### 🎯 Mock Interview Simulation
- AI-powered mock interviews based on your resume
- Dynamic conversation with interview questions tailored to your experience
- Natural dialogue with follow-up questions
- Comprehensive feedback on interview performance

## How to Use

1. **Upload Resume**: 
   - Select your PDF resume file using the upload area
   - Optionally paste a job description for more tailored feedback

2. **Review Redacted Text**:
   - Examine the automatically redacted text
   - Make any necessary edits or corrections
   - Click "Approve and Send to Claude" when ready

3. **Review Claude's Analysis**:
   - Read through the detailed resume analysis
   - Note recommendations for improvement
   - Click "Start Mock Interview" to practice interview skills, customized to your resume and job description

4. **Practice Mock Interview**:
   - Respond to the interviewer's questions in the chat interface
   - Engage in natural dialogue
   - Click "End Interview & Get Feedback" when done
   - Review comprehensive interview feedback tailored to your resume and job description

## Privacy and Security

This tool prioritizes user privacy and security by redacting personal identifiers commonly found in resumes. This allows privacy-minded job-seekers to easily avoid passing personally identifiable information, like names, addresses, phone numbers, and emails into potential training data.

## Technical Details
This project was built using:
- Claude API
- Python/Flask
- HTML/CSS/Bootstrap

## Deployment
This project can be downloaded and run locally. Setup instructions are as follows:

   1. Install relevant dependencies with `pip install -r requirements.txt`.
   2. Run the app locally with `flask --app privacv run`.

## Future Enhancements
In the future, we hope to enhance our redaction process and test out more use cases to make it more robust. We also hope to provide more functionality, such as cover letter help, technical interview practice, and web deployment.

## Acknowledgments
Thank you to the Anthropic and WiCS team that made this hackathon happen! We had so much fun building this weekend `:)` 