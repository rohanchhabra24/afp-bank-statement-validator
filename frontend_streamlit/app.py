import streamlit as st
import requests
import base64
import json
import pandas as pd
import os

st.set_page_config(page_title="AFP Validator", layout="wide")

st.title("📄 AFP Bank Statement Validator")
st.markdown("Upload your AFP/PDF statement to validate anomalies like column bleeds, impossible dates, and balance drifts.")

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
                    st.error(f"Server returned error code {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
