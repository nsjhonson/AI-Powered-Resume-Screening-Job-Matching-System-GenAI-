import streamlit as st
import requests
import json

# Configuration
import os
# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for UI styling
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dcdcdc;
        text-align: center;
        color: #333333; /* Force text to be dark on white background */
    }
    .metric-card h3 {
        color: #333333 !important;
        margin: 0;
        padding: 0;
        font-size: 1.2rem;
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
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Process Resume"):
            with st.spinner("Parsing and vectorizing resume..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                try:
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
tab1, tab2 = st.tabs(["Single Job Match", "Multi-Job Comparison"])

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
