from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

def create_sample_statement(filename):
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    
    # Headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 500, "Date")
    c.drawString(150, 500, "Transaction Details")
    c.drawString(450, 500, "Debits (£)")
    c.drawString(550, 500, "Credits (£)")
    c.drawString(650, 500, "Balance (£)")
    
    c.line(50, 490, 750, 490)
    
    c.setFont("Helvetica", 10)
    
    # Row 1
    c.drawString(50, 470, "01 FEB")
    c.drawString(150, 470, "Account Balance")
    c.drawString(650, 470, "5,665.75")
    
    # Row 2 (Anomaly: stray '1' in Transaction Details far right)
    c.drawString(50, 450, "1 FEB")
    c.drawString(150, 450, "Interest Charge")
    c.drawString(350, 450, "1")  # Stray '1'
    c.drawString(450, 450, "59.39")
    c.drawString(650, 450, "5,725.14")
    
    # Row 3
    c.drawString(50, 430, "1 MAR")
    c.drawString(150, 430, "Interest Charge")
    c.drawString(450, 430, "51.99")
    c.drawString(650, 430, "5,777.13")
    
    # Row 4
    c.drawString(50, 410, "1 MAR")
    c.drawString(150, 410, "Payment by Direct Credit")
    c.drawString(550, 410, "250.02")
    c.drawString(650, 410, "5,527.11")

    # Row 5 (Anomaly: Balance math error)
    c.drawString(50, 390, "31 MAR")
    c.drawString(150, 390, "Payment by Direct Credit")
    c.drawString(550, 390, "250.02")
    c.drawString(650, 390, "5,277.09") # Actually should be 5,527.11 - 250.02 = 5277.09... Wait, credit adds to balance! 
    # If credit adds, 5527.11 + 250.02 = 5777.13. So 5277.09 is mathematically wrong in the statement! Let's reproduce the screenshot exactly.
    
    c.save()

if __name__ == "__main__":
    create_sample_statement("test_statement.pdf")
