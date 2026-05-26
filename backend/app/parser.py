import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
from .models import TransactionRow

def parse_pdf(file_path: str) -> List[TransactionRow]:
    doc = fitz.open(file_path)
    rows = []
    
    # Very naive table extraction using bounding boxes
    for page_num in range(len(doc)):
        page = doc[page_num]
        words = page.get_text("words")  # Returns (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        
        # Group words by line (y-coordinate clustering)
        lines = []
        words.sort(key=lambda w: w[1]) # Sort by y0
        
        current_line = []
        current_y = -1
        for w in words:
            if current_y == -1 or abs(w[1] - current_y) < 5: # 5px tolerance
                current_line.append(w)
                if current_y == -1:
                    current_y = w[1]
            else:
                lines.append(current_line)
                current_line = [w]
                current_y = w[1]
                
        if current_line:
            lines.append(current_line)
            
        # Parse lines into TransactionRows based on x-coordinates
        # Note: In a real scenario, column boundaries would be dynamic or configured.
        # This is a naive hardcoded mapping for the POC
        # Date: 0-100, Party: 100-300, Debit: 300-400, Credit: 400-500, Balance: 500-600
        
        row_idx = 1
        for line in lines:
            data = {}
            bboxes = {}
            
            for w in line:
                x0, y0, x1, y1, text, _, _, _ = w
                
                # Assign to columns based on x0
                col_name = None
                if 0 <= x0 < 130:
                    col_name = 'Date'
                elif 130 <= x0 < 400:
                    col_name = 'Party'  # We'll map Transaction Details to Party to minimize other code changes
                elif 400 <= x0 < 500:
                    col_name = 'Debit'
                elif 500 <= x0 < 600:
                    col_name = 'Credit'
                elif 600 <= x0 < 800:
                    col_name = 'Balance'
                    
                if col_name:
                    if col_name in data:
                        data[col_name] += ' ' + text
                        # Expand bbox
                        old_bbox = bboxes[col_name]
                        bboxes[col_name] = [min(old_bbox[0], x0), min(old_bbox[1], y0), max(old_bbox[2], x1), max(old_bbox[3], y1)]
                    else:
                        data[col_name] = text
                        bboxes[col_name] = [x0, y0, x1, y1]
            
            if data: # Only add if we found something
                rows.append(TransactionRow(
                    row_index=row_idx,
                    data=data,
                    bboxes=bboxes
                ))
                row_idx += 1
                
    return rows

def parse_afk(file_path: str) -> List[TransactionRow]:
    # Mock parser for AFK/AFP files since we don't have afplib installed
    # We will try to read it as plain text and construct mock rows
    # In a real scenario, this would use a proper AFP parser like afplib
    rows = []
    
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
            
        # We just create a few mock rows to show the pipeline works
        rows.append(TransactionRow(
            row_index=1,
            data={'Date': '10/10/2024', 'Party': 'Opening Balance', 'Debit': '0.00', 'Credit': '100.00', 'Balance': '100.00'},
            bboxes={'Date': [10,720,60,730], 'Balance': [100,720,150,730]}
        ))
        
        # Row 2 with a balance drift
        rows.append(TransactionRow(
            row_index=2,
            data={'Date': '11/10/2024', 'Party': 'AFK Upload Error', 'Debit': '50.00', 'Credit': '0.00', 'Balance': '999.00'},
            bboxes={'Date': [10,700,60,710], 'Balance': [100,700,150,710]}
        ))
    except Exception as e:
        print(f"Failed to read AFK: {e}")
        
    return rows

