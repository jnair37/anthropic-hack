from claude_utils import call_claude

# simple test prompt
test_prompt = "Give me 3 resume tips for someone applying to software engineering jobs."

# call Claude and print response
response = call_claude(test_prompt)
print(response)
