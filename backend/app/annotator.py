import fitz
from typing import List
from .models import ValidationIssue
import os

def annotate_pdf(input_path: str, output_path: str, issues: List[ValidationIssue]):
    doc = fitz.open(input_path)
    
    # We'll just annotate the first page for simplicity, or iterate
    # Assuming bounding boxes are on page 0 since our parser doesn't track page number yet.
    # We should really track page numbers in TransactionRow bboxes!
    # For POC, let's just annotate page 0 for all issues.
    
    page = doc[0]
    
    for issue in issues:
        if issue.bbox:
            rect = fitz.Rect(issue.bbox)
            
            # Draw highlight
            annot = page.add_rect_annot(rect)
            
            # Color coding
            if issue.severity == 'CRITICAL':
                annot.set_colors(stroke=(1, 0, 0)) # Red
            elif issue.severity == 'WARNING':
                annot.set_colors(stroke=(1, 0.65, 0)) # Amber/Orange
            else:
                annot.set_colors(stroke=(0, 0, 1)) # Blue for INFO
                
            annot.update()
            
            # Add text annotation nearby
            text_rect = fitz.Rect(rect.x1 + 5, rect.y0, rect.x1 + 100, rect.y1)
            page.insert_text(text_rect.tl, f"[{issue.rule}]", color=(1, 0, 0) if issue.severity == 'CRITICAL' else (1, 0.65, 0), fontsize=8)
            
    doc.save(output_path)
    doc.close()
    
    return output_path
