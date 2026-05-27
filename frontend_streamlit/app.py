import streamlit as st
import requests
import base64
import json
import pandas as pd
import os

st.set_page_config(page_title="Financial Document Intelligence", layout="wide")

# Minimal Light CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    .css-1d391kg {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 24px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    h1 {
        color: #0f3b7b !important;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .stButton>button {
        background-color: #0f3b7b;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(15, 59, 123, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #0a2956;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(15, 59, 123, 0.3);
    }
    
    [data-testid="stMetricValue"] {
        color: #0f3b7b;
    }
</style>
""", unsafe_allow_html=True)

st.title("📑 Financial Document Intelligence POC")
st.markdown("Upload any multi-page bank-related document (PDF/AFP/AFK). Our AI agent will intelligently extract and validate the contents.")

API_URL = "http://127.0.0.1:8000/validate"

uploaded_file = st.file_uploader("Upload AFP, AFK, or PDF document", type=["pdf", "afp", "afk"])

if uploaded_file is not None:
    st.info("File uploaded. Click 'Validate' to begin analysis.")
    if st.button("🔍 Validate Document"):
        with st.spinner("Analyzing document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "error" in data:
                        st.error(f"Error during validation: {data['error']}")
                    else:
                        st.success("Validation complete!")
                        
                        issues = data.get("issues", [])
                        pdf_base64 = data.get("annotated_pdf", "")
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("Annotated Document")
                            if pdf_base64:
                                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="800" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.warning("No PDF returned.")
                                
                        with col2:
                            st.subheader("Validation Issues")
                            if not issues:
                                st.success("No anomalies found!")
                            else:
                                df = pd.DataFrame(issues)
                                # Color code by severity
                                def color_severity(val):
                                    color = 'red' if val == 'CRITICAL' else 'orange' if val == 'WARNING' else 'blue'
                                    return f'color: {color}'
                                
                                st.dataframe(df.style.applymap(color_severity, subset=['severity']))
                                
                                # Download JSON report
                                json_str = json.dumps(issues, indent=2)
                                st.download_button(
                                    label="Download JSON Report",
                                    data=json_str,
                                    file_name="validation_report.json",
                                    mime="application/json"
                                )
                else:
                    try:
                        error_data = response.json()
                        st.error(f"Backend Error: {error_data.get('error', 'Unknown Error')}")
                    except:
                        st.error(f"Server returned error code {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
