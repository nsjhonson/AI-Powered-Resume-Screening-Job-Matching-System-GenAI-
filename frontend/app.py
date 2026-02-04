import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie
import plotly.express as px

# Configuration
import os
# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

# --- AUTHENTICATION SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load assets
lottie_login = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_jcikwtux.json")
lottie_success = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_5tkzkblw.json")

def auth_flow():
    st.markdown("""
        <style>
        /* Modern Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
            color: #FFFFFF;
        }
        
        /* Glassmorphism Card */
        div[data-testid="stForm"], div[data-baseweb="tab-panel"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Inputs */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] div {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px; 
            color: #FFFFFF;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(to right, #00d2ff, #3a7bd5) !important;
            color: white !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if lottie_login:
            st_lottie(lottie_login, height=200, key="login_anim")
        st.markdown("<h1 style='text-align: center;'>🔐 Recruiter Portal</h1>", unsafe_allow_html=True)
        
        tab_login, tab_register, tab_forgot = st.tabs(["Login", "Register", "Forgot Password"])
        
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    try:
                        res = requests.post(f"{BACKEND_URL}/auth/login", json={"username": username, "password": password})
                        if res.status_code == 200:
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = username
                            st.success("Login Successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                sec_q = st.selectbox("Security Question", [
                    "What is your pet's name?",
                    "What city were you born in?",
                    "What is your mother's maiden name?"
                ])
                sec_a = st.text_input("Security Answer")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if reg_submit:
                    if new_user and new_pass and sec_a:
                        try:
                            payload = {
                                "username": new_user,
                                "password": new_pass,
                                "security_question": sec_q,
                                "security_answer": sec_a
                            }
                            res = requests.post(f"{BACKEND_URL}/auth/register", json=payload)
                            if res.status_code == 200:
                                st.success("Account Created! Please Login.")
                            else:
                                st.error(f"Error: {res.json().get('detail')}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
                    else:
                        st.warning("Please fill all fields.")

        with tab_forgot:
            st.write("Reset Password Step 1")
            f_user = st.text_input("Enter Username", key="f_user")
            if st.button("Check User"):
                try:
                    res = requests.post(f"{BACKEND_URL}/auth/get-security-question", json={"username": f_user})
                    if res.status_code == 200:
                        st.session_state['reset_user'] = f_user
                        st.session_state['reset_q'] = res.json()['security_question']
                    else:
                        st.error("User not found")
                except:
                    st.error("Connection error")
            
            if 'reset_user' in st.session_state:
                st.info(f"Question: {st.session_state['reset_q']}")
                with st.form("reset_form"):
                    ans = st.text_input("Answer")
                    new_p = st.text_input("New Password", type="password")
                    reset_submit = st.form_submit_button("Reset Password")
                    
                    if reset_submit:
                        try:
                            payload = {"username": st.session_state['reset_user'], "security_answer": ans, "new_password": new_p}
                            res = requests.post(f"{BACKEND_URL}/auth/reset-password", json=payload)
                            if res.status_code == 200:
                                st.success("Password Reset! Please Login.")
                                del st.session_state['reset_user']
                            else:
                                st.error(res.json().get('detail'))
                        except:
                            st.error("Error resetting password")

if not st.session_state['logged_in']:
    auth_flow()
    st.stop()
    
# Clean Logout Button in Sidebar
with st.sidebar:
    st.write(f"👤 User: **{st.session_state.get('username', 'Admin')}**")
    if st.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- APP CONTENT STARTS HERE ---

# Fetch Data from DB
def fetch_all_candidates():
    try:
        response = requests.get(f"{BACKEND_URL}/candidates")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

# Initialize session state with DB data if empty
if 'batch_data' not in st.session_state or not st.session_state['batch_data']:
    db_data = fetch_all_candidates()
    if db_data:
        st.session_state['batch_data'] = db_data

# Custom CSS for UI styling (Global)
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
    }
    
    /* Metrics Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card h3 {
        color: #00d2ff !important;
        margin: 0;
        padding: 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .metric-card p {
        color: #E0E0E0 !important;
        margin-top: 5px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: #FFFFFF;
        padding: 10px 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(to right, #00d2ff, #3a7bd5) !important;
        color: white !important;
        font-weight: bold;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }

    .high-score { color: #28a745; font-weight: bold; }
    .medium-score { color: #ffc107; font-weight: bold; }
    .low-score { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Powered Resume Screening System")
st.markdown("### Intelligent Job Matching using GenAI & RAG")

# Sidebar for Resume Upload
with st.sidebar:
    st.header("Step 1: Upload Details")
    uploaded_file = st.file_uploader("Upload Resume (PDF or ZIP)", type=["pdf", "zip"])
    
    if uploaded_file is not None:
        if st.button("Process Resume(s)"):
            with st.spinner("Processing..."):
                try:
                    if uploaded_file.name.endswith(".zip"):
                        # Batch Upload
                        files = {"file": (uploaded_file.name, uploaded_file, "application/zip")}
                        response = requests.post(f"{BACKEND_URL}/upload-zip", files=files)
                        if response.status_code == 200:
                            st.success("Batch processing complete!")
                            st.session_state['batch_data'] = response.json()
                            st.info(f"Processed {len(st.session_state['batch_data'])} resumes.")
                        else:
                            st.error(f"Error processing batch: {response.text}")
                    else:
                        # Single PDF Upload
                        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                        response = requests.post(f"{BACKEND_URL}/upload-resume", files=files)
                        if response.status_code == 200:
                            st.success("Resume uploaded successfully!")
                            data = response.json()
                            st.session_state['filename'] = data['filename']
                            st.session_state['extracted_data'] = data.get('extracted_data', {})
                        else:
                            st.error(f"Error uploading resume: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # Show Extracted Info Preview
    if 'extracted_data' in st.session_state:
        st.divider()
        st.subheader("Extracted Profile")
        data = st.session_state['extracted_data']
        st.write(f"**Name:** {data.get('name', 'Unknown')}")
        st.write(f"**Experience:** {data.get('experience_years', 0)} years")
        st.write("**Skills:**")
        st.write(", ".join(data.get('skills', [])))

# Main Area for Job Matching
# Main Area for Job Matching
st.header("Step 2: Job Matching")

# Tabs for Single vs Multi Job Mode
# Tabs for Single vs Multi Job Mode
tab1, tab2, tab3 = st.tabs(["Single Job Match", "Multi-Job Comparison", "Analytics Dashboard"])

# --- ANALYTICS TAB ---
with tab3:
    st.header("📊 Talent Pool Analytics (Persistent Database)")
    if 'batch_data' not in st.session_state or not st.session_state['batch_data']:
        st.info("No candidates found in the database. Upload resumes to build your talent pool.")
        # Try fetching again
        if st.button("Refresh Results"):
            st.session_state['batch_data'] = fetch_all_candidates()
            st.rerun()
    else:
        batch_data = st.session_state['batch_data']
        if not batch_data:
            st.warning("No valid data found in the uploaded batch.")
        else:
            # 1. Total Candidates
            st.metric("Total Candidates Processed", len(batch_data))
            
            # Prepare Dataframes
            import pandas as pd
            all_skills = []
            experiences = []
            
            for item in batch_data:
                data = item.get('extracted_data', {})
                if data:
                    # Flatten skills
                    all_skills.extend(data.get('skills', []))
                    experiences.append(data.get('experience_years', 0))
            
            # 2. Top Skills Interactive Chart
            if all_skills:
                st.subheader("Top Skills Found")
                skill_counts = pd.Series(all_skills).value_counts().head(10).reset_index()
                skill_counts.columns = ['Skill', 'Count']
                
                fig = px.bar(skill_counts, x='Skill', y='Count', color='Count',
                             color_continuous_scale='Viridis', title="Most Common Candidate Skills")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
            
            # 3. Experience Distribution Area Chart
            if experiences:
                st.subheader("Experience Level Distribution")
                exp_df = pd.DataFrame(experiences, columns=["Years of Experience"])
                
                fig2 = px.histogram(exp_df, x="Years of Experience", nbins=10, 
                                    template="plotly_dark", title="Experience Distribution")
                fig2.update_traces(marker_color='#00d2ff')
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig2, use_container_width=True)
                
            st.divider()
            
            # 4. Data Table
            st.subheader("Candidate Overview")
            overview_data = []
            for item in batch_data:
                d = item.get('extracted_data', {})
                overview_data.append({
                    "Name": d.get('name', 'Unknown'),
                    "Experience": d.get('experience_years', 0),
                    "Skills (Count)": len(d.get('skills', [])),
                    "Filename": item.get('filename')
                })
            st.dataframe(pd.DataFrame(overview_data), use_container_width=True)

# --- SINGLE JOB MODE ---
with tab1:
    job_description = st.text_area("Enter Job Description", height=200, placeholder="Paste the job description here...", key="single_jd")
    match_btn = st.button("Match Candidate", type="primary", use_container_width=True, key="single_btn")

    if match_btn and job_description:
        with st.spinner("AI is analyzing the match..."):
            try:
                payload = {"job_description": job_description, "min_score": 0.0}
                response = requests.post(f"{BACKEND_URL}/match-job", json=payload)
                
                if response.status_code == 200:
                    results = response.json().get("matches", [])
                    current_file = st.session_state.get('filename')
                    
                    if current_file:
                        match = next((m for m in results if m['filename'] == current_file), None)
                    else:
                        match = results[0] if results else None
                        
                    if match:
                        st.subheader("Match Results")
                        # --- Score Visualization ---
                        score = match['score']
                        if score >= 75:
                            score_color = "#28a745"
                            match_label = "Strong Match"
                        elif score >= 50:
                            score_color = "#ffc107"
                            match_label = "Moderate Match"
                        else:
                            score_color = "#dc3545"
                            match_label = "Low Match"

                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 10px; border: 2px solid {score_color}; border-radius: 10px;">
                                <h2 style="color: {score_color}; margin: 0;">{score}%</h2>
                                <p style="margin: 0; font-weight: bold;">{match_label}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with c2:
                            st.caption(f"Match Confidence: {score}/100")
                            st.progress(int(score))
                            st.write(f"**AI Reason:** {match.get('ai_explanation', 'No explanation provided.')}")

                        st.divider()

                        # --- Skills Breakdown ---
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"""
                            <div class="metric-card" style="border-left: 5px solid #28a745;">
                                <h3>✅ Matched Skills</h3>
                                <p style="font-size: 1.1rem;">{', '.join(match.get('matched_skills', [])) if match.get('matched_skills') else 'None'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_b:
                            st.markdown(f"""
                            <div class="metric-card" style="border-left: 5px solid #dc3545;">
                                <h3>❌ Missing Skills</h3>
                                <p style="font-size: 1.1rem;">{', '.join(match.get('missing_skills', [])) if match.get('missing_skills') else 'None'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # --- PDF Report Generation ---
                        from fpdf import FPDF
                        from datetime import datetime
                        
                        # Define function locally to capture state
                        def create_pdf_report(match_data, candidate_data):
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_text_color(50, 50, 50)
                            
                            # Header
                            pdf.set_font('Arial', 'B', 20)
                            pdf.cell(0, 10, 'AI Resume Screening Report', ln=True, align='C')
                            pdf.ln(10)
                            
                            # Metadata
                            pdf.set_font('Arial', '', 10)
                            pdf.cell(0, 5, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
                            pdf.ln(5)
                            
                            # Candidate Info
                            pdf.set_fill_color(240, 240, 240)
                            pdf.rect(10, 35, 190, 25, 'F')
                            pdf.set_y(40)
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(30, 8, "Candidate:", 0)
                            pdf.set_font('Arial', '', 12)
                            pdf.cell(100, 8, candidate_data.get('name', 'Unknown'), 0, ln=True)
                            
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(30, 8, "Experience:", 0)
                            pdf.set_font('Arial', '', 12)
                            pdf.cell(100, 8, f"{candidate_data.get('experience_years', 0)} years", 0, ln=True)
                            pdf.ln(10)

                            # Match Score
                            score_val = match_data['score']
                            if score_val >= 75: color = (40, 167, 69)
                            elif score_val >= 50: color = (255, 193, 7)
                            else: color = (220, 53, 69)
                            
                            pdf.set_draw_color(*color)
                            pdf.set_fill_color(*color)
                            pdf.rect(10, 70, 190, 15, 'DF')
                            
                            pdf.set_y(73)
                            pdf.set_font('Arial', 'B', 14)
                            pdf.set_text_color(255, 255, 255)
                            pdf.cell(0, 10, f"Match Score: {score_val}%", 0, 1, 'C')
                            pdf.set_text_color(50, 50, 50)
                            pdf.ln(10)

                            # AI Analysis
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(0, 10, "Broad AI Reasoning:", ln=True)
                            pdf.set_font('Arial', '', 11)
                            # Handle encoding
                            explanation = match_data.get('ai_explanation', 'No explanation.').encode('latin-1', 'replace').decode('latin-1')
                            pdf.multi_cell(0, 6, explanation)
                            pdf.ln(5)
                            
                            # Skills
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(0, 10, "Matched Skills:", ln=True)
                            pdf.set_font('Arial', '', 11)
                            pdf.multi_cell(0, 6, ", ".join(match_data.get('matched_skills', [])))
                            pdf.ln(5)
                            
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(0, 10, "Missing Skills:", ln=True)
                            pdf.set_font('Arial', '', 11)
                            pdf.multi_cell(0, 6, ", ".join(match_data.get('missing_skills', [])))
                            
                            return pdf.output(dest='S').encode('latin-1')

                        # Generate and Button
                        try:
                            pdf_bytes = create_pdf_report(match, data)
                            st.download_button(
                                label="⬇️ Download Screening Report (PDF)",
                                data=pdf_bytes,
                                file_name=f"Screening_Report_{data.get('name', 'candidate').replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF: {e}")

                        # --- Step 3: Interview Question Generator ---
                        st.subheader("Step 3: Interview Preparation")
                        if st.button("Generate Interview Questions", type="secondary"):
                            with st.spinner("Generating targeted questions..."):
                                try:
                                    q_payload = {"resume_data": data, "job_description": job_description}
                                    q_response = requests.post(f"{BACKEND_URL}/generate-questions", json=q_payload)
                                    if q_response.status_code == 200:
                                        questions = q_response.json().get("questions", [])
                                        st.success("Questions Generated!")
                                        for i, q in enumerate(questions, 1):
                                            st.markdown(f"**Q{i}.** {q}")
                                    else:
                                        st.error(f"Error: {q_response.text}")
                                except Exception as e:
                                    st.error(f"Connection error: {e}")
                        
                        # --- Step 4: Salary Estimation ---
                        st.subheader("Step 4: Salary Insights (Beta)")
                        if st.button("Estimate Market Salary", type="secondary"):
                            with st.spinner("Analyzing market rates..."):
                                try:
                                    s_payload = {"resume_data": data, "job_description": job_description}
                                    s_response = requests.post(f"{BACKEND_URL}/estimate-salary", json=s_payload)
                                    if s_response.status_code == 200:
                                        salary_data = s_response.json()
                                        st.info(f"**Estimated Range:** {salary_data.get('salary_range', 'N/A')}")
                                        st.caption(f"Reasoning: {salary_data.get('reasoning', 'N/A')}")
                                    else:
                                        st.error(f"Error: {s_response.text}")
                                except Exception as e:
                                    st.error(f"Connection error: {e}")
                        
                        # --- Step 5: Email Automation ---
                        st.subheader("Step 5: Action")
                        
                        # Prepare email content
                        candidate_name = data.get('name', 'Candidate')
                        subject = f"Interview Invitation: {candidate_name} for Job Role"
                        body = f"Hi {candidate_name},%0D%0A%0D%0AWe reviewed your profile and were impressed by your skills. Your match score is {match.get('score')}%25!%0D%0A%0D%0AWe would like to invite you for an interview.%0D%0A%0D%0ARegards,%0D%0AHiring Team"
                        
                        mailto_link = f"mailto:?subject={subject}&body={body}"
                        
                        st.link_button("📧 Send Interview Invite", mailto_link, type="primary")

                    else:
                        st.warning("No matches found.")
                else:
                    st.error(f"Error matching: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- MULTI JOB MODE ---
with tab2:
    st.info("Paste multiple Job Descriptions separated by '---' (three dashes) to compare them.")
    multi_jd_text = st.text_area("Enter Multiple Job Descriptions", height=300, placeholder="Job 1 Description...\n\n---\n\nJob 2 Description...", key="multi_jd")
    compare_btn = st.button("Compare Jobs", type="primary", use_container_width=True, key="multi_btn")
    
    if compare_btn and multi_jd_text:
        # Split JDs
        jds = [jd.strip() for jd in multi_jd_text.split('---') if jd.strip()]
        
        if not jds:
            st.warning("No valid job descriptions found. Please separate them with '---'.")
        else:
            results_list = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, jd in enumerate(jds):
                status_text.text(f"Analyzing Job {i+1}/{len(jds)}...")
                try:
                    payload = {"job_description": jd, "min_score": 0.0}
                    response = requests.post(f"{BACKEND_URL}/match-job", json=payload)
                    
                    if response.status_code == 200:
                        matches = response.json().get("matches", [])
                        current_file = st.session_state.get('filename')
                        match = next((m for m in matches if m['filename'] == current_file), matches[0] if matches else None)
                        
                        if match:
                            results_list.append({
                                "Job ID": f"Job {i+1}",
                                "Score": match['score'],
                                "Status": "Strong" if match['score'] >= 75 else "Moderate" if match['score'] >= 50 else "Low",
                                "Matched Skills": len(match.get('matched_skills', [])),
                                "Missing Skills": len(match.get('missing_skills', [])),
                                "Full Result": match  # hidden from table but used for details
                            })
                except Exception as e:
                    st.error(f"Error processing Job {i+1}: {e}")
                
                progress_bar.progress((i + 1) / len(jds))
            
            status_text.empty()
            
            if results_list:
                # Sort best first
                results_list.sort(key=lambda x: x['Score'], reverse=True)
                
                st.subheader("🏆 Comparison Result")
                
                # Display Summary Table
                import pandas as pd
                df = pd.DataFrame([
                    {k: v for k, v in r.items() if k != 'Full Result'} 
                    for r in results_list
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # CSV Export
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name='job_comparison_results.csv',
                    mime='text/csv',
                )
                
                # Best Match Highlight
                best = results_list[0]
                st.success(f"**Best Match:** {best['Job ID']} with {best['Score']}% Score")
                
                # Detailed view
                with st.expander("View Detailed Breakdown"):
                    for res in results_list:
                        m = res['Full Result']
                        st.markdown(f"### {res['Job ID']} - {res['Score']}%")
                        st.write(f"**Reasoning:** {m.get('ai_explanation', 'N/A')}")
                        st.write(f"**Matched:** {', '.join(m.get('matched_skills', []))}")
                        st.write(f"**Missing:** {', '.join(m.get('missing_skills', []))}")
                        st.markdown("---")
            else:
                st.warning("No matches could be generated.")
