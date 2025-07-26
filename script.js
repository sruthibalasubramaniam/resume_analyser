document.addEventListener('DOMContentLoaded', () => {
    const resumeForm = document.getElementById('resume-form');
    const resumeFileInput = document.getElementById('resume-file');
    const fileNameSpan = document.getElementById('file-name');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results-container');
    const errorMessageDiv = document.getElementById('error-message');
    const overallScore = document.getElementById('overall-score');
    const quickView = document.getElementById('quick-view');
    const candidateName = document.getElementById('candidate-name');
    const candidateEmail = document.getElementById('candidate-email');
    const candidatePhone = document.getElementById('candidate-phone');
    const candidateSkill = document.getElementById('candidate-skill');
    const analysisElement = document.getElementById('full-analysis');

    // --- THIS IS THE MISSING PIECE OF LOGIC ---
    // This event listener's only job is to update the file name on the screen.
    resumeFileInput.addEventListener('change', () => {
        if (resumeFileInput.files.length > 0) {
            fileNameSpan.textContent = resumeFileInput.files[0].name;
        } else {
            fileNameSpan.textContent = 'No file selected';
        }
    });
    // ------------------------------------------

    resumeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (resumeFileInput.files.length === 0) {
            showError("Please select a PDF file to analyze.");
            return;
        }

        const formData = new FormData();
        formData.append('resume', resumeFileInput.files[0]);

        // Reset UI
        loader.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        errorMessageDiv.classList.add('hidden');

        try {
            const response = await fetch('http://127.0.0.1:5000/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            showError(`An error occurred: ${error.message}`);
        } finally {
            loader.classList.add('hidden');
        }
    });

    function displayResults(data) {
        overallScore.textContent = `Overall Score: ${data.score}/100`;
        
        if (data.details) {
            candidateName.textContent = data.details.name || 'Not Found';
            candidateEmail.textContent = data.details.email || 'Not Found';
            candidatePhone.textContent = data.details.phone || 'Not Found';
            candidateSkill.textContent = data.details.main_skill || 'Not Found';
            quickView.classList.remove('hidden');
        } else {
            quickView.classList.add('hidden');
        }

        analysisElement.innerHTML = marked.parse(data.full_analysis);
        resultsContainer.classList.remove('hidden');
    }

    function showError(message) {
        errorMessageDiv.textContent = message;
        errorMessageDiv.classList.remove('hidden');
    }
});