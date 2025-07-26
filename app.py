import fitz  # PyMuPDF
import os
import re
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Initialize Flask App and CORS ---
app = Flask(__name__)
# CORS allows our frontend (running on a different port) to talk to this backend
CORS(app)

# --- Configure Gemini API Key at the start ---
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set!")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"CRITICAL: Configuration Error: {e}")
    # In a real app, you might exit or handle this more gracefully
    # For now, we'll let it fail when a request comes in.

# --- Your Existing Functions (no changes needed) ---
def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

def generate_analysis(resume_text: str) -> str:
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    prompt_template ="""
    You are an expert career coach and professional resume reviewer. Your task is to analyze the provided resume text, give it a comprehensive evaluation, and provide a score. The resume text has been extracted from a PDF and may have some formatting inconsistencies; please parse it to the best of your ability.

    Please provide your analysis in the following structured format, ensuring the score is clearly marked:

    **Overall Score: [Score]/100**
    *A brief, high-level summary of the resume's key strengths and primary areas for improvement.*

    ---
    ### Detailed Breakdown & Actionable Feedback

    **1. Clarity, Formatting, and ATS Compatibility (Score: /20):**
    *   Feedback: *Evaluate the overall readability, professional tone, and structure.*
    *   Suggestions: *Provide specific advice to improve formatting and clarity.*

    **2. Professional Summary / Objective (Score: /10):**
    *   Feedback: *Analyze the summary or objective. Is it impactful?*
    *   Suggestions: *Suggest improvements to make the summary more powerful.*

    **3. Work Experience (Score: /30):**
    *   Feedback: *Evaluate the description of roles and responsibilities. Are they focused on achievements?*
    *   Suggestions: *Give examples of how to rephrase bullet points to be more results-oriented.*

    **4. Skills Section (Score: /20):**
    *   Feedback: *Assess the organization and relevance of the skills listed.*
    *   Suggestions: *Recommend adding or removing skills, or organizing them more effectively.*

    **5. Education & Projects (Score: /20):**
    *   Feedback: *Check if the education section is clear and concise.*
    *   Suggestions: *Provide advice on how to better present educational background.*

    ---

    **Resume text to analyze is provided below:**
    """
    full_prompt = f"{prompt_template}\n\n{resume_text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred during analysis generation: {e}")
        return ""

def extract_details(resume_text: str) -> dict:
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    prompt = f"""
    You are a highly accurate data extraction tool. Your task is to analyze the following resume text and extract specific pieces of information.

    **Instructions:**
    1.  Extract the full name of the candidate.
    2.  Extract the email address.
    3.  Extract the phone number.
    4.  Identify the 2 most impactful **technical hard skill**. 
        -   A technical hard skill is a specific, teachable proficiency in a tool, software, programming language, or methodology.
        -   **Analyze the entire resume**, including work experience and skills sections, to find the skill that is most central to the candidate's value.
        -   **Examples of good, specific skills to extract:**  `AutoCAD`, `React.js`, `AWS CloudFormation`, `QuickBooks`, `SolidWorks`, `SQL`, `Financial Modeling`, `C++`, `Agile Methodology`.
        -   **You MUST AVOID vague fields or soft skills.** Examples of what **NOT** to extract:` Python` , `Mechanical Engineering` (this is a field), `Communication` (soft skill), `Leadership` (soft skill), `Problem-Solving` (soft skill), `Marketing` (a field), `Management` (a broad category).

    Provide the output *only* in a valid JSON format, with no extra text or explanations. Use the following structure:
    {{
        "name": "Jane Doe",
        "email": "jane.doe@email.com",
        "phone": "123-456-7890",
        "main_skill": "AutoCAD"
    }}

    **Resume Text to Analyze:**
    ---
    {resume_text}
    """
    try:
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred during detail extraction: {e}")
        return None

# --- New Flask API Endpoint ---
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    """Receives a resume, processes it, and returns the analysis."""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    resume_file = request.files['resume']
    
    # Save the file temporarily to be read by fitz
    temp_filename = "temp_resume.pdf"
    resume_file.save(temp_filename)

    # --- Run your existing logic ---
    resume_text = extract_text_from_pdf(temp_filename)
    if not resume_text:
        os.remove(temp_filename)
        return jsonify({"error": "Could not extract text from PDF"}), 500

    analysis_text = generate_analysis(resume_text)
    if not analysis_text:
        os.remove(temp_filename)
        return jsonify({"error": "Failed to generate analysis from AI"}), 500
    
    # Parse the score
    score = 0
    match = re.search(r"Overall Score:\s*(\d{1,3})", analysis_text)
    if match:
        score = int(match.group(1))

    # Conditionally extract details
    candidate_details = None
    if score > 55:
        candidate_details = extract_details(resume_text)

    # Clean up the temporary file
    os.remove(temp_filename)

    # --- Return everything in a single JSON response ---
    return jsonify({
        "full_analysis": analysis_text,
        "score": score,
        "details": candidate_details # This will be null if score <= 55
    })

# --- To run the Flask server ---
if __name__ == "__main__":
    # Use port 5000, a common port for local development
    app.run(debug=True, port=5000)





  