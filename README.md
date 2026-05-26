# AFP Bank Statement Validator

An intelligent validation pipeline and UI for parsing, validating, and annotating bank statements to detect anomalies such as column bleeds, impossible dates, missing values, and balance arithmetic drifts.

## 🚀 Quick Start Guide

Follow these exact steps to run this project on a brand new system.

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Clone the Repository
Open your terminal and clone the repository:
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd "AFK Validator"
```
*(Note: Replace `<YOUR_GITHUB_REPO_URL>` with your actual GitHub repository URL once uploaded).*

### 3. Set Up a Virtual Environment (Recommended)
It is best practice to run this in an isolated environment to avoid dependency conflicts.
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 4. Install Dependencies
Install all required libraries for the FastAPI backend and Streamlit frontend:
```bash
pip install -r backend/requirements.txt
pip install reportlab streamlit requests
```

### 5. Generate Test Data (Optional)
To verify the system works, you can generate a mock bank statement (`test_statement.pdf`) with carefully planted anomalies (like a stray '1' causing a column bleed):
```bash
python generate_sample.py
```

### 6. Run the Application
You can start both the FastAPI backend and the Streamlit UI with a single command using the provided script.

First, ensure the script is executable (Mac/Linux only):
```bash
chmod +x run.sh
```

Then, run the app:
```bash
./run.sh
```
The Streamlit interface will automatically open in your browser (usually at `http://localhost:8501`). You can now upload `test_statement.pdf` and view the annotated results live!

### 🧪 Running the System Test via Terminal
If you just want to test the backend engine without launching the UI, you can run the automated pipeline test:
```bash
python test_pipeline.py
```
This script will parse `test_statement.pdf`, run all validation rules (including the `ColumnBleedValidator`), print the detected issues to your terminal, and generate the visually highlighted `outputs/test_annotated.pdf`.
