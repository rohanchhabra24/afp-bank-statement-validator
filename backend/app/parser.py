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
        
        # Extract raw words with their coordinates
        words = page.get_text("words")
        
        # Sort words primarily by y-coordinate, then by x-coordinate for a natural reading order
        words.sort(key=lambda w: (w[1], w[0]))
        
        # Filter out very small or irrelevant text if necessary, but here we just pass all tokens
        tokens = []
        for w in words:
            tokens.append({
                "text": w[4],
                "bbox": [round(w[0], 2), round(w[1], 2), round(w[2], 2), round(w[3], 2)]
            })
            
        if not tokens:
            continue
            
        # Call OpenAI to intelligently parse the tokens into structured rows
        import os
        import json
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please add it to your .env file or environment.")
            
        prompt = f"""
You are an expert financial document parser. You will be provided with a JSON array of text tokens and their physical bounding boxes [x0, y0, x1, y1] extracted from a bank statement page.
Your task is to reconstruct the transaction table rows intelligently. 
The expected columns are: "Date", "Party" (Transaction Details), "Debit", "Credit", "Balance".
If a value is missing or empty, omit the key or set it to "".
IMPORTANT: You MUST also provide the combined bounding boxes for each column you extract. A combined bounding box is [min_x, min_y, max_x, max_y] covering all tokens in that cell.

Respond ONLY with a raw JSON array (no markdown code blocks) of objects matching this exact structure:
[
  {{
    "row_index": 1,
    "data": {{"Date": "01 FEB", "Party": "Account Balance", "Debit": "", "Credit": "", "Balance": "5,665.75"}},
    "bboxes": {{"Date": [50.0, 450.0, 90.0, 460.0], "Party": [150.0, 450.0, 250.0, 460.0], "Balance": [650.0, 450.0, 710.0, 460.0]}}
  }}
]

Tokens:
{json.dumps(tokens)}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # Using GPT-4o for maximum accuracy per user request
                messages=[
                    {"role": "system", "content": "You are a precise data extraction agent. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            result_text = response.choices[0].message.content.strip()
            # Clean up potential markdown formatting if the LLM ignores instructions
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
                
            extracted_data = json.loads(result_text.strip())
            
            for row_data in extracted_data:
                rows.append(TransactionRow(**row_data))
                
        except Exception as e:
            print(f"Failed to parse page {page_num} using OpenAI: {e}")
            raise e
                
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

