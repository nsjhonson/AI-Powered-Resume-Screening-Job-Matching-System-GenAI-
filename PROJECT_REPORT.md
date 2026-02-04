# 📑 Project Report: AI-Powered Resume Screening & Job Matching System

## 1. Problem Statement
**The Hiring Challenge**:
In the modern recruitment landscape, HR professionals are overwhelmed by the sheer volume of applications. Traditional Applicant Tracking Systems (ATS) rely on **keyword matching**, which is often inaccurate. They reject qualified candidates who use different synonyms and accept underqualified ones who simply "keyword stuff" their resumes. This results in:
*   **High Time-to-Hire**: Recruiters spend hours manually filtering resumes.
*   **Human Bias**: Unconscious bias can affect initial screening.
*   **Missed Talent**: Good candidates are overlooked due to poor formatting or missing exact keywords.

## 2. Why We Chose This Project
We chose to build an **AI-Powered System** to solve these inefficiencies using **Generative AI (GenAI)**. Unlike basic regex or keyword matching, GenAI (specifically Large Language Models) can understand **context and semantics**.
*   **Goal**: To build a system that thinks like a human recruiter but works at the speed of software.
*   **Impact**: drastically reduces screening time while improving the quality of shortlisted candidates.

## 3. Challenges Faced & Solutions

### 🛑 Challenge 1: API Rate Limits (Quota Exhaustion)
*   **Problem**: We used the `Gemini-2.0-Flash` free tier. During testing, we frequently hit the `429 Resource Exhausted` error because the LLM was called too rapidly.
*   **Solution**: We implemented **Robust Retry Logic** in the backend. The system now automatically waits and retries requests with exponential backoff (up to 6 times) before failing, ensuring stability even under load.

### 🛑 Challenge 2: Unstructured PDF Data
*   **Problem**: Resumes come in various layouts (single column, double column). Standard text extractors often scrambled the read order, merging lines from different columns.
*   **Solution**: We used a combination of `pypdf` for raw extraction and, crucially, **Prompt Engineering**. We instructed the AI to "act as a resume parser" to intelligently reconstruct the structured JSON data (Name, Skills, Experience) from the raw, sometimes messy, text.

### 🛑 Challenge 3: Deployment & Connectivity
*   **Problem**: Connecting a cloud-hosted Frontend (Streamlit) to a separate Backend (FastAPI) and managing sensitive API keys securely.
*   **Solution**:
    *   We decoupled the architecture.
    *   We used **Environment Variables** (`BACKEND_URL`, `GOOGLE_API_KEY`) to manage configuration.
    *   We created a specific `DEPLOYMENT.md` guide to handle the specific secret management required by platforms like Render and Streamlit Cloud.

## 4. Project Output
The final product is a fully functional web application that delivers:
1.  **Automated Parsing**: Upload a PDF, and the system instantly extracts profile details.
2.  **Semantic Match Scoring**: Returns a percentage score (0-100%) based on *skills and experience relevance*, not just keywords.
3.  **Actionable Insights**:
    *   **Visual Gauge**: Color-coded scores (Green/Yellow/Red).
    *   **Gap Analysis**: Clearly lists "Matched Skills" vs. "Missing Skills".
4.  **Reporting**: Generates a downloadable **PDF Screening Report** for HR documentation.
5.  **Multi-Job Capabilities**: Can screen a single candidate against multiple potential job roles simultaneously to find the best fit.

## 5. Future Scope & Roadmap
To scale this project into a commercial-grade product, we have identified three phases of enhancements:

### 🟢 Phase 1: Immediate Enhancements (Quick Wins)
*   **Interview Question Generator**: (Implemented) Auto-generate 5 technical questions based on missing skills.
*   **Salary Insight**: AI-driven market salary estimation based on candidate experience and role.
*   **Accessibility**: Improved Dark/Light mode support for better usability.

### 🟡 Phase 2: Professional Features (Intermediate)
*   **Batch Processing**: Support for uploading a `.zip` file containing 50+ resumes for mass screening.
*   **Analytics Dashboard**: A visual dashboard showing "Top Skills in Talent Pool", "Average Experience", and "Score Distribution".
*   **Data Export**: Ability to export ranking tables to **Excel/CSV** for HR integration.

### 🔴 Phase 3: Enterprise Integration (Advanced)
*   **Database Integration**: persistent storage (PostgreSQL/MongoDB) to build a searchable "Talent Pool" of past candidates.
*   **Email Automation**: One-click "Send Interview Invite" feature for high-scoring candidates.
*   **User Authentication**: Secure login/signup for multiple recruiters to manage their own job postings.

---
*Submitted by: [Your Name/Team Name]*
