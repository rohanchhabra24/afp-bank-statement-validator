from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor

def create_sample_statement(filename):
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # 1. Header / Logo Area
    # Draw a mock logo (Blue rectangle + Text)
    c.setFillColor(HexColor("#0f3b7b"))
    c.rect(50, height - 70, 40, 40, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(58, height - 60, "R")
    
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 55, "Royal Banking Corp")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 70, "Everyday Banking Division")
    
    # Customer Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Mr. John Doe")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 135, "123 Business Avenue")
    c.drawString(50, height - 150, "London, UK")
    c.drawString(50, height - 165, "SW1A 1AA")
    
    # Statement Details Box (Top Right)
    c.setFont("Helvetica", 10)
    c.drawString(width - 250, height - 120, "Account Number:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 120, "070070/34327574")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 250, height - 140, "Statement Date:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 140, "2 DECEMBER 2023")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 250, height - 160, "Page:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 160, "Page 2 of 3")
    
    # Greeting / Legal text
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 210, "Dear John Doe, here is your requested statement.")
    c.drawString(50, height - 225, "This information must not be used for redemption purposes. A settlement figure is available on request.")
    
    # 2. Table Header
    y = height - 260
    c.setFillColor(HexColor("#e8ebf0"))
    c.rect(50, y-10, width - 100, 25, fill=1, stroke=0)
    
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 11)
    
    # Column positions to match the screenshot roughly
    date_x = 70
    details_x = 200
    debits_x = width - 350
    credits_x = width - 250
    balance_x = width - 150
    
    c.drawString(date_x, y, "Date")
    c.drawString(details_x, y, "Transaction Details")
    c.drawString(debits_x, y, "Debits (£)")
    c.drawString(credits_x, y, "Credits (£)")
    c.drawString(balance_x, y, "Balance (£)")
    
    # Table Lines
    c.setLineWidth(0.5)
    c.setStrokeColor(HexColor("#cccccc"))
    c.line(50, y-10, width - 50, y-10) # bottom header line
    c.line(50, y+15, width - 50, y+15) # top header line
    
    # 3. Table Rows
    c.setFont("Helvetica", 10)
    y -= 30
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(date_x, y, "2023")
    c.setFont("Helvetica", 10)
    y -= 15
    
    # Row 1
    c.drawString(date_x, y, "01 FEB")
    c.drawString(details_x, y, "Account Balance")
    c.drawString(balance_x, y, "5,665.75")
    y -= 20
    
    # Row 2 (Anomaly: stray '1' in Transaction Details far right)
    c.drawString(date_x, y, "1 FEB")
    c.drawString(details_x, y, "Interest Charge")
    c.drawString(details_x + 180, y, "1")  # Stray '1' visually separated
    c.drawString(debits_x + 15, y, "59.39")
    c.drawString(balance_x, y, "5,725.14")
    y -= 20
    
    # Row 3
    c.drawString(date_x, y, "1 MAR")
    c.drawString(details_x, y, "Interest Charge")
    c.drawString(debits_x + 15, y, "51.99")
    c.drawString(balance_x, y, "5,777.13")
    y -= 20
    
    # Row 4
    c.drawString(date_x, y, "1 MAR")
    c.drawString(details_x, y, "Payment by Direct Credit")
    c.drawString(details_x, y-12, "from 070246/44131938")
    c.drawString(credits_x + 15, y, "250.02")
    c.drawString(balance_x, y, "5,527.11")
    y -= 35
    
    # Row 5 (Math error anomaly)
    c.drawString(date_x, y, "31 MAR")
    c.drawString(details_x, y, "Payment by Direct Credit")
    c.drawString(details_x, y-12, "from 070246/44131938")
    c.drawString(credits_x + 15, y, "250.02")
    c.drawString(balance_x, y, "5,277.09")
    y -= 35
    
    # Row 6
    c.drawString(date_x, y, "1 APR")
    c.drawString(details_x, y, "Interest Charge")
    c.drawString(debits_x + 15, y, "55.48")
    c.drawString(balance_x, y, "5,332.57")
    y -= 20
    
    # Footer lines / closing table
    c.line(50, y, width - 50, y)
    
    # Notices Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 30, "Notices")
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 45, "If you notice any anomalies in your account, please contact our support team immediately.")
    
    c.save()

def create_credit_card_statement(filename):
    c = canvas.Canvas(filename, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # 1. Header / Logo Area
    c.setFillColor(HexColor("#2a2a2a"))
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "TITANIUM CREDIT SERVICES")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 65, "Monthly Billing Statement")
    
    # Customer Details
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Ms. Jane Smith")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 135, "456 Corporate Blvd")
    c.drawString(50, height - 150, "New York, NY 10001")
    
    # Statement Details Box (Top Right)
    c.setFont("Helvetica", 10)
    c.drawString(width - 250, height - 120, "Card Number:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 120, "**** **** **** 9012")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 250, height - 140, "Statement Date:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 140, "15 MAY 2024")
    
    # 2. Table Header
    y = height - 220
    c.setFillColor(HexColor("#f0f0f0"))
    c.rect(50, y-10, width - 100, 25, fill=1, stroke=0)
    
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 11)
    
    date_x = 70
    details_x = 200
    debits_x = width - 350
    credits_x = width - 250
    balance_x = width - 150
    
    c.drawString(date_x, y, "Date")
    c.drawString(details_x, y, "Transaction Details")
    c.drawString(debits_x, y, "Purchases ($)")
    c.drawString(credits_x, y, "Payments ($)")
    c.drawString(balance_x, y, "Balance ($)")
    
    # 3. Table Rows
    c.setFont("Helvetica", 10)
    y -= 30
    
    # Row 1: Opening Balance
    c.drawString(date_x, y, "01 MAY")
    c.drawString(details_x, y, "Previous Balance")
    c.drawString(balance_x, y, "1,200.00")
    y -= 20
    
    # Row 2: Valid Purchase
    c.drawString(date_x, y, "05 MAY")
    c.drawString(details_x, y, "Apple Store Fifth Ave")
    c.drawString(debits_x + 15, y, "150.00")
    c.drawString(balance_x, y, "1,350.00")
    y -= 20
    
    # Row 3: Anomaly - Stray character in Amount (Column Bleed)
    c.drawString(date_x, y, "10 MAY")
    c.drawString(details_x, y, "Uber Rides")
    c.drawString(debits_x + 15, y, "25.00 A") # Stray 'A'
    c.drawString(balance_x, y, "1,375.00")
    y -= 20
    
    # Row 4: Valid Payment
    c.drawString(date_x, y, "12 MAY")
    c.drawString(details_x, y, "Online Payment - Thank You")
    c.drawString(credits_x + 15, y, "1,000.00")
    c.drawString(balance_x, y, "375.00")
    y -= 20
    
    # Row 5: Anomaly - Impossible Date
    c.drawString(date_x, y, "31 NOV") # Impossible date
    c.drawString(details_x, y, "Late Fee")
    c.drawString(debits_x + 15, y, "35.00")
    c.drawString(balance_x, y, "410.00")
    y -= 20
    
    c.save()

if __name__ == "__main__":
    create_sample_statement("professional_statement.pdf")
    create_credit_card_statement("credit_card_statement.pdf")
