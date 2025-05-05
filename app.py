import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json

from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


##GEmini pro response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text 


##
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range (len(reader.pages)):
        page = reader.pages[page]
        text+= str(page.extract_text())
    return text


## Prompt Template



input_prompt = """
Hey, Act Like a skilled or very experience ATS(Application Tracking System) with a deep understanding of tech fields, software engineering, data science, data analyst and big data engineer.
Your task is to evaluate the resume based on the job description.
You must consider the job market is very competitive and you should provide best assistance to the user.
Assign the percentage Matchinng based on job description and missing keywords in the resume.
resume:{text}
description:{job_description}
I want the response in a single string having the structure as below:
{{
  "JD Match":"{{jd_match}}%",
  "Missing Keywords":"{{missing_keywords}}",
  "Resume Score":"{{resume_score}}",
  "Feedback":"{{feedback}}"
}}
"""

##streamlit app
st.title("ATS Resume Evaluator")
st.text("Upload your resume and job description to get the ATS evaluation.")
job_description = st.text_area("Job Description", height=200)
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
submit_button = st.button("Evaluate")


if submit_button:
    if uploaded_file is not None and job_description:
        resume_text = input_pdf_text(uploaded_file)
        raw_response = get_gemini_response(input_prompt.format(text=resume_text, job_description=job_description))
        # st.json(response)  # Display the response in JSON format
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(cleaned)
            st.subheader("Evaluation Result")
            st.json(parsed)
        except json.JSONDecodeError as e:
            st.error("Error parsing response as JSON. Showing raw response:")
            st.text(raw_response)
    else:
        st.warning("Please upload a PDF resume and enter a job description.")