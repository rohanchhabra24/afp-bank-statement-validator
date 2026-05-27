import re
from typing import List, Dict, Any
from dateutil.parser import parse
from .models import TransactionRow, ValidationIssue

class BaseValidator:
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        raise NotImplementedError

class DateFormatValidator(BaseValidator):
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        for row in rows:
            date_str = row.data.get('Date', '')
            if not date_str:
                continue
            
            # Use dateutil.parse to aggressively check if the string represents a valid date.
            # This allows flexible formats like '01 FEB', '12-12-2023', '2 DECEMBER 2024'.
            try:
                # fuzzy=True allows ignoring surrounding characters if necessary
                parse(date_str, dayfirst=True, fuzzy=False)
            except ValueError:
                issues.append(ValidationIssue(
                    rule='DateFormatValidator',
                    severity='CRITICAL',
                    row_index=row.row_index,
                    column='Date',
                    raw_value=date_str,
                    message='Invalid or impossible date format detected',
                    bbox=row.bboxes.get('Date')
                ))
        return issues

class AmountColumnValidator(BaseValidator):
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        for row in rows:
            for col in ['Debit', 'Credit', 'Balance']:
                val = row.data.get(col, '')
                if not val:
                    continue
                
                # Check for sign mismatch (e.g., negative debit)
                if '-' in str(val) and col in ['Debit', 'Credit']:
                    issues.append(ValidationIssue(
                        rule='AmountColumnValidator',
                        severity='WARNING',
                        row_index=row.row_index,
                        column=col,
                        raw_value=str(val),
                        message=f'Unexpected negative sign in {col}',
                        bbox=row.bboxes.get(col)
                    ))
                
                # We could add column bleed detection here if we had neighbor data
        return issues

class BalanceReconciler(BaseValidator):
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        running_balance = 0.0
        
        for i, row in enumerate(rows):
            debit_str = str(row.data.get('Debit', '0')).replace(',', '')
            credit_str = str(row.data.get('Credit', '0')).replace(',', '')
            balance_str = str(row.data.get('Balance', '0')).replace(',', '')
            
            try:
                debit = float(debit_str) if debit_str.strip() else 0.0
                credit = float(credit_str) if credit_str.strip() else 0.0
                balance = float(balance_str) if balance_str.strip() else 0.0
            except ValueError:
                continue # Skip if we can't parse amounts
                
            if i == 0:
                running_balance = balance
                continue
                
            expected_balance = running_balance - debit + credit
            
            if abs(expected_balance - balance) > 0.01:
                issues.append(ValidationIssue(
                    rule='BalanceReconciler',
                    severity='CRITICAL',
                    row_index=row.row_index,
                    column='Balance',
                    raw_value=balance_str,
                    message=f'Balance drift. Expected {expected_balance:.2f}, got {balance:.2f}',
                    bbox=row.bboxes.get('Balance')
                ))
            
            running_balance = balance
            
        return issues

class NullFieldChecker(BaseValidator):
    def __init__(self, required_columns: List[str]):
        self.required_columns = required_columns
        
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        for row in rows:
            for col in self.required_columns:
                val = row.data.get(col, '')
                if not str(val).strip():
                    issues.append(ValidationIssue(
                        rule='NullFieldChecker',
                        severity='CRITICAL',
                        row_index=row.row_index,
                        column=col,
                        raw_value='',
                        message=f'Missing value in mandatory column: {col}',
                        bbox=row.bboxes.get(col)
                    ))
        return issues

class ColumnBleedValidator(BaseValidator):
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        for row in rows:
            party_val = str(row.data.get('Party', ''))
            
            # Simple heuristic: if the text column ends with a space followed by a digit, 
            # and that digit is far right (which we simulate by just checking for isolated trailing digits 
            # that look like they belong to amounts).
            # e.g., "Interest Charge 1"
            import re
            if re.search(r'\s+\d+$', party_val):
                issues.append(ValidationIssue(
                    rule='ColumnBleedValidator',
                    severity='CRITICAL',
                    row_index=row.row_index,
                    column='Transaction Details',
                    raw_value=party_val,
                    message='Possible column bleed. Stray number found at the end of transaction details.',
                    bbox=row.bboxes.get('Party')
                ))
        return issues

class ValidationEngine:
    def __init__(self):
        self.validators = [
            DateFormatValidator(),
            AmountColumnValidator(),
            BalanceReconciler(),
            NullFieldChecker(required_columns=['Date', 'Balance']),
            ColumnBleedValidator()
        ]
        
    def run(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        all_issues = []
        for validator in self.validators:
            issues = validator.validate(rows)
            all_issues.extend(issues)
        return all_issues
