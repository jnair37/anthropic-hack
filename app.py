import streamlit as st
import redactr as rdr

st.title("Claude Resume Reviewer")
st.write("Upload your resume in .pdf format. " \
"This tool will redact personal information from your resume and then Claude " \
"will review it and give you tailored feedback.")

uploaded_resume = st.file_uploader("Resume upload (PDF)", type=['pdf'])
# uploaded_job = st.file_uploader("Upload job description (optional)", type=['pdf', 'txt'])

if uploaded_resume is not None:
    st.write("Resume uploaded:", uploaded_resume.name)
    # st.write(type(uploaded_resume))

    # Create the button for running redaction
    if st.button("Redact Resume"):
        with st.spinner("Redacting personal information..."):
            # Call the redaction function from your teammate's module
            try:
                st.write("placeholder text, redaction theoretically occurs")
                redacted_text = rdr.redact_pdf(uploaded_resume)
                
                # Display redacted content
                st.success("Redaction complete!")
                st.subheader("Redacted Resume")
                st.text_area("Redacted content", redacted_text, height=300)
                
                # # Option to send to Claude (will be implemented by third teammate)
                # if uploaded_job is not None and st.button("Analyze fit with Claude"):
                #     st.info("Sending to Claude for analysis...")
                #     # This would call your other teammate's Claude integration
                #     # claude_module.analyze_fit(redacted_text, uploaded_job)
            
            except Exception as e:
                st.error(f"Error during redaction: {str(e)}")