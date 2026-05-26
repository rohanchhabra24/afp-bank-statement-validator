from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
import base64

from .parser import parse_pdf, parse_afk
from .validator import ValidationEngine
from .annotator import annotate_pdf

app = FastAPI(title="AFP Validator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

engine = ValidationEngine()

@app.post("/validate")
async def validate_document(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_annotated.pdf")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Phase 1: Parse based on extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in ['.afk', '.afp']:
            rows = parse_afk(input_path)
            # For POC with afk files, we might not be able to annotate a PDF if it wasn't generated.
            # Let's generate a dummy PDF or handle the exception in annotator
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(output_path)
            c.drawString(100, 750, f"Processed {ext.upper()} File")
            c.save()
            # Try to annotate the dummy PDF
            annotate_pdf(output_path, output_path, engine.run(rows))
        else:
            rows = parse_pdf(input_path)
            
        # Phase 2: Validate
        issues = engine.run(rows)
        
        # Phase 3: Annotate (only if it was a PDF, or we generated a dummy one)
        if ext not in ['.afk', '.afp']:
            annotate_pdf(input_path, output_path, issues)
        
        # Prepare response
        with open(output_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
            
        return {
            "status": "success",
            "issues": [issue.dict() for issue in issues],
            "annotated_pdf": pdf_base64
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def read_root():
    return {"message": "AFP Validator API is running"}
