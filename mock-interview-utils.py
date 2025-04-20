# app.py
import os
import json
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_file
from werkzeug.utils import secure_filename
import anthropic
from typing import Dict, List, Optional, Tuple

class ResumeContext:
    """A class to manage resume context for the Model Context Protocol."""
    
    def __init__(self, resume_text: str, job_title: str = ""):
        """Initialize with the applicant's resume text and target job title."""
        self.resume_text = resume_text
        self.job_title = job_title
        self.parsed_skills = None
        self.parsed_experience = None
        self.applicant_summary = None
    
    def get_context_message(self) -> Dict:
        """Returns the formatted context message for Claude."""
        job_context = f"Target position: {self.job_title}" if self.job_title else ""
        
        return {
            "role": "user",
            "content": f"""<context>
            # APPLICANT RESUME
            {self.resume_text}

            {job_context}
            </context>

            I'll be acting as the interviewer for this candidate. For each interview question I send, conduct a mock interview while keeping the candidate's resume in mind. Respond as if you are the candidate based on their resume information."""
        }
    
    def update_context(self, skills: List[str], experience: Dict, summary: str):
        """Update the parsed context data."""
        self.parsed_skills = skills
        self.parsed_experience = experience
        self.applicant_summary = summary


class MockInterviewSystem:
    """A system that uses MCP to conduct mock interviews while maintaining resume context."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with the Anthropic API key."""
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20240620"
        self.resume_context = None
        self.conversation_id = None
        self.interview_history = []
    
    def set_resume_context(self, resume_text: str, job_title: str = ""):
        """Set the resume context for the interview."""
        self.resume_context = ResumeContext(resume_text, job_title)
        
        # Parse the resume to enrich our context
        system_message = "You are an expert at parsing resumes. Extract key skills, experience details, and provide a brief professional summary."
        
        response = self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=[{"role": "user", "content": resume_text}],
            max_tokens=1000
        )
        
        # Parse the response to update our context
        try:
            parsed_data = json.loads(response.content)
            self.resume_context.update_context(
                skills=parsed_data.get("skills", []),
                experience=parsed_data.get("experience", {}),
                summary=parsed_data.get("summary", "")
            )
        except:
            # If not valid JSON, just use the text response
            self.resume_context.update_context(
                skills=[],
                experience={},
                summary=response.content
            )
        
        # Start a conversation with the context
        response = self.client.messages.create(
            model=self.model,
            messages=[self.resume_context.get_context_message()],
            system="You are an AI trained to simulate job candidates in mock interviews based on their resumes. Respond as the candidate would, staying true to their experience and skills.",
        )
        
        # Store the conversation ID for future interactions
        self.conversation_id = response.id
    
    def ask_interview_question(self, question: str) -> str:
        """Ask an interview question while maintaining resume context."""
        if not self.resume_context:
            raise ValueError("You must set a resume context first with set_resume_context()")
        
        # Format the interview question
        interview_prompt = f"""<interview_question>
{question}
</interview_question>

Please respond as the candidate would based on their resume information."""
        
        # Use the Anthropic API with conversation ID to maintain context
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": interview_prompt}],
            system="You are an AI trained to simulate job candidates in mock interviews based on their resumes. Respond as the candidate would, staying true to their experience and skills.",
        )
        
        # Add to interview history
        self.interview_history.append((question, response.content))
        
        return response.content
    
    def get_interview_summary(self) -> str:
        """Get a summary of the interview performance."""
        if not self.interview_history:
            return "No interview has been conducted yet."
        
        questions_and_answers = "\n\n".join([
            f"Q: {q}\nA: {a}" for q, a in self.interview_history
        ])
        
        summary_prompt = f"""<interview_review>
The following is a transcript of the mock interview:

{questions_and_answers}
</interview_review>

Please provide a summary of the interview performance, highlighting:
1. Strengths demonstrated
2. Areas for improvement
3. Overall impression
4. Advice for the real interview"""
        
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": summary_prompt}],
            system="You are an expert HR interviewer who provides constructive feedback on interview performances.",
            max_tokens=1500
        )
        
        return response.content
    
    def generate_interview_questions(self, num_questions: int = 5) -> List[str]:
        """Generate relevant interview questions based on the resume and job title."""
        if not self.resume_context:
            raise ValueError("You must set a resume context first with set_resume_context()")
        
        job_info = f"for the position of {self.resume_context.job_title}" if self.resume_context.job_title else ""
        
        generate_prompt = f"""Based on the candidate's resume, generate {num_questions} tailored interview questions {job_info}.
Focus on technical skills, experience validation, behavioral scenarios, and problem-solving abilities.
Return the questions as a JSON array of strings."""
        
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": generate_prompt}],
            system="You are an expert technical interviewer who creates tailored interview questions based on candidate resumes.",
            max_tokens=1000
        )
        
        try:
            # Try to parse as JSON
            questions = json.loads(response.content)
            if isinstance(questions, list):
                return questions
            elif isinstance(questions, dict) and "questions" in questions:
                return questions["questions"]
        except:
            # If not valid JSON, try to extract questions manually
            questions = []
            lines = response.content.split("\n")
            for line in lines:
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
                    # Remove the number and any quotes
                    question = line.strip().split(".", 1)[1].strip().strip('"\'')
                    questions.append(question)
            
            if questions:
                return questions
            else:
                # Last resort: just return the raw content
                return [response.content]


def redact_pdf(file):
    """Placeholder for PDF redaction functionality"""
    # In a real implementation, this would process the PDF
    # For now, just read the file content if it's a text file
    try:
        content = file.read().decode('utf-8')
        return content
    except:
        return "Unable to process file. Please ensure it's in text format."


def get_full_resume_review(resume_text, job_description):
    """Generate a full resume review using Claude API"""
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        prompt = f"""Please provide a comprehensive review of this resume in relation to the specified job description:

## RESUME:
{resume_text}

## JOB DESCRIPTION:
{job_description}

Analyze the following:
1. Overall match between resume and job requirements
2. Key strengths and how they align with the position
3. Potential gaps or areas where the resume could be stronger
4. Suggestions for improvement
5. Any key achievements that should be highlighted

Please be specific and actionable in your feedback."""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system="You are an expert resume reviewer and career coach with deep knowledge of hiring practices across industries.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        
        return response.content
    except Exception as e:
        return f"Error generating resume review: {str(e)}"
