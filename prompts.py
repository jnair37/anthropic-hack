def feedback_prompt(resume_text):
    return f"""You're a resume reviewer. Ignore the fact that it is redacted. Please analyze the resume below and provide:

1. A readability score out of 100
2. Sections that are vague or unclear
3. Suggestions to improve vocabulary or phrasing
4. 1–2 formatting improvements

Resume:
{resume_text}
"""
