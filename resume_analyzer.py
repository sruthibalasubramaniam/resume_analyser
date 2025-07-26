import fitz  # PyMuPDF
import os
import re
import json
import google.generativeai as genai

# --- Function 1: Extract Text from PDF ---
def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a given PDF file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

# --- Function 2: Generate the Full Resume Analysis ---
def generate_analysis(resume_text: str) -> str:
    """
    Analyzes and scores the provided resume text using the Gemini API.

    Returns:
        The full analysis text as a single string.
    """
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    
    prompt_template = """
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

    print("🤖 Generating resume analysis... This may take a moment.")
    
    try:
        response = model.generate_content(full_prompt)
        # Instead of streaming and printing, return the complete text
        print("✅ Analysis generated.")
        return response.text
    except Exception as e:
        print(f"An error occurred during content generation: {e}")
        return ""

# --- Function 3: Extract Specific Details (Name, Contact, Main Skill) ---
# --- Function 3: Extract Specific Details (Name, Contact, Main Skill) ---
# --- REPLACE your old function with this new, improved version ---
def extract_details(resume_text: str) -> dict:
    """
    Uses the Gemini API to extract specific details from the resume text with a
    strong focus on a specific, technical hard skill.
    
    Returns:
        A dictionary containing the extracted details.
    """
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest") # Using the faster model for extraction
    
    # --- THIS IS THE IMPROVED PROMPT ---
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
    
    print("🕵️‍♂️ Extracting key details with a focus on a specific technical skill...")
    
    try:
        # Configuration to ensure the model outputs JSON
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        
        details = json.loads(response.text)
        print("✅ Details extracted.")
        return details
    except Exception as e:
        print(f"An error occurred during detail extraction or JSON parsing: {e}")
        return None

# --- Main Orchestrator ---
def main():
    """Main function to run the resume analysis and extraction process."""
    
    # --- Configure API Key ---
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set!")
        genai.configure(api_key=api_key)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # --- Step 1: Extract text from the PDF ---
    pdf_file_path = "resume.pdf"
    print(f"📄 Extracting text from '{pdf_file_path}'...")
    resume_text = extract_text_from_pdf(pdf_file_path)
    if not resume_text or not resume_text.strip():
        print("Could not extract text from the PDF. Exiting.")
        return
    print("✅ Text extracted successfully.")

    # --- Step 2: Get the full analysis from the AI ---
    analysis_text = generate_analysis(resume_text)
    if not analysis_text:
        print("Failed to generate analysis. Exiting.")
        return
    
    # Also print the full analysis for the user
    print("\n--- Full Resume Analysis ---\n")
    print(analysis_text)
    print("\n--------------------------\n")

    # --- Step 3: Parse the score and decide whether to proceed ---
    score = 0
    # Use regular expression to find the score reliably
    match = re.search(r"Overall Score:\s*(\d{1,3})", analysis_text)
    if match:
        score = int(match.group(1))
        print(f"📊 Parsed Score: {score}/100")
    else:
        print("Could not parse the score from the analysis.")
        return

    # --- Step 4: If score is high enough, extract and print details ---
    if score > 35:
        print(f"🎉 Score is above 55! Proceeding with detail extraction.")
        candidate_details = extract_details(resume_text)
        
        if candidate_details:
            print("\n--- Candidate Quick View ---")
            print(f"  👤 Name:         {candidate_details.get('name', 'Not Found')}")
            print(f"  📧 Email:        {candidate_details.get('email', 'Not Found')}")
            print(f"  📞 Phone:        {candidate_details.get('phone', 'Not Found')}")
            print(f"  🌟 Main Skill:   {candidate_details.get('main_skill', 'Not Found')}")
            print("----------------------------\n")
    else:
        print(f"❌ Score of {score} is not above 55. No further details will be extracted.")


if __name__ == "__main__":
    main()