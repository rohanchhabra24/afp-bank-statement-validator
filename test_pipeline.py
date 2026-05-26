import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from backend.app.parser import parse_pdf
from backend.app.validator import ValidationEngine
from backend.app.annotator import annotate_pdf

def test():
    file_path = "test_statement.pdf"
    output_path = "outputs/test_annotated.pdf"
    
    rows = parse_pdf(file_path)
    print(f"Parsed {len(rows)} rows.")
    for r in rows:
        print(r)
        
    engine = ValidationEngine()
    issues = engine.run(rows)
    
    print(f"Found {len(issues)} issues:")
    for i in issues:
        print(i)
        
    annotate_pdf(file_path, output_path, issues)
    print(f"Annotated PDF saved to {output_path}")

if __name__ == "__main__":
    test()
