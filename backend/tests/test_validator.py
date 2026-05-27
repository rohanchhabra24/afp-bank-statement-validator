import pytest
from backend.app.models import TransactionRow
from backend.app.validator import ValidationEngine

@pytest.fixture
def engine():
    return ValidationEngine()

def test_valid_transactions(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '01 FEB', 'Party': 'Opening', 'Debit': '', 'Credit': '', 'Balance': '1000.00'}, bboxes={}),
        TransactionRow(row_index=2, data={'Date': '02 FEB', 'Party': 'Deposit', 'Debit': '', 'Credit': '500.00', 'Balance': '1500.00'}, bboxes={}),
        TransactionRow(row_index=3, data={'Date': '05 FEB', 'Party': 'Withdrawal', 'Debit': '200.00', 'Credit': '', 'Balance': '1300.00'}, bboxes={}),
    ]
    issues = engine.run(rows)
    assert len(issues) == 0

def test_date_format_edge_cases(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': 'Date', 'Balance': '0'}, bboxes={}), # Header, should pass
        TransactionRow(row_index=2, data={'Date': '31 FEB 2024', 'Balance': '0'}, bboxes={}), # Impossible date, should fail
        TransactionRow(row_index=3, data={'Date': 'Unknown', 'Balance': '0'}, bboxes={}), # Invalid string, should fail
    ]
    issues = engine.run(rows)
    date_issues = [i for i in issues if i.rule == 'DateFormatValidator']
    assert len(date_issues) == 2
    assert "31 FEB" in date_issues[0].raw_value
    assert "Unknown" in date_issues[1].raw_value

def test_balance_reconciler_micro_drift(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '01 FEB', 'Balance': '1000.00'}, bboxes={}),
    # A tiny fraction drift (e.g. OCR missing a decimal or misreading 1000.00 + 0.10 = 1000.12)
    TransactionRow(row_index=2, data={'Date': '02 FEB', 'Credit': '0.10', 'Balance': '1000.12'}, bboxes={}),
    ]
    issues = engine.run(rows)
    drift_issues = [i for i in issues if i.rule == 'BalanceReconciler']
    assert len(drift_issues) == 1
    assert drift_issues[0].row_index == 2

def test_column_bleed_stray_digits(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '01 FEB', 'Party': 'Amazon Purchase 2', 'Balance': '100.00'}, bboxes={}), # Stray 2 at end
        TransactionRow(row_index=2, data={'Date': '02 FEB', 'Party': '1 Amazon Purchase', 'Balance': '100.00'}, bboxes={}), # Stray 1 at beginning
        TransactionRow(row_index=3, data={'Date': '03 FEB', 'Party': 'Amazon Purchase', 'Balance': '100.00'}, bboxes={})  # Clean
    ]
    issues = engine.run(rows)
    bleed_issues = [i for i in issues if i.rule == 'ColumnBleedValidator']
    assert len(bleed_issues) == 2
    assert bleed_issues[0].row_index == 1
    assert bleed_issues[1].row_index == 2

def test_stray_characters_in_amount_columns(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '01 FEB', 'Debit': '100.00 A', 'Balance': '100.00'}, bboxes={}), # Stray letter
        TransactionRow(row_index=2, data={'Date': '02 FEB', 'Credit': '100 00', 'Balance': '200.00'}, bboxes={}), # Separated numbers
        TransactionRow(row_index=3, data={'Date': '03 FEB', 'Credit': '100.00', 'Balance': '300.00'}, bboxes={}), # Clean
    ]
    issues = engine.run(rows)
    amount_issues = [i for i in issues if i.rule == 'AmountColumnValidator' and 'Stray character' in i.message]
    assert len(amount_issues) == 2
    assert amount_issues[0].row_index == 1
    assert amount_issues[1].row_index == 2

def test_null_mandatory_fields(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '', 'Party': 'Missing Date', 'Balance': '100.00'}, bboxes={}),
        TransactionRow(row_index=2, data={'Date': '01 FEB', 'Party': 'Missing Balance', 'Balance': ''}, bboxes={}),
    ]
    issues = engine.run(rows)
    null_issues = [i for i in issues if i.rule == 'NullFieldChecker']
    assert len(null_issues) == 2

def test_negative_sign_in_amounts(engine):
    rows = [
        TransactionRow(row_index=1, data={'Date': '01 FEB', 'Debit': '-50.00', 'Balance': '100.00'}, bboxes={}),
    ]
    issues = engine.run(rows)
    amount_issues = [i for i in issues if i.rule == 'AmountColumnValidator']
    assert len(amount_issues) == 1
    assert "negative sign" in amount_issues[0].message
