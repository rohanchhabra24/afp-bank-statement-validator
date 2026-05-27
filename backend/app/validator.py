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
            date_str = str(row.data.get('Date', '')).strip()
            
            # Skip empty strings or literal table headers (like the word "Date")
            if not date_str or date_str.lower() == 'date':
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
                    message='Invalid or impossible date format detected (possible column bleed)',
                    bbox=row.bboxes.get('Date')
                ))
        return issues

class AmountColumnValidator(BaseValidator):
    def validate(self, rows: List[TransactionRow]) -> List[ValidationIssue]:
        issues = []
        for row in rows:
            for col in ['Debit', 'Credit', 'Balance']:
                val = str(row.data.get(col, '')).strip()
                if not val:
                    continue
                
                # Check for sign mismatch (e.g., negative debit)
                if '-' in val and col in ['Debit', 'Credit']:
                    issues.append(ValidationIssue(
                        rule='AmountColumnValidator',
                        severity='WARNING',
                        row_index=row.row_index,
                        column=col,
                        raw_value=val,
                        message=f'Unexpected negative sign in {col}',
                        bbox=row.bboxes.get(col)
                    ))
                
                # Check for stray characters or column bleeds (e.g. "100.00 A" or "100 1")
                clean_val = val.replace(',', '')
                if not re.match(r'^-?\d+(?:\.\d+)?$', clean_val):
                    issues.append(ValidationIssue(
                        rule='AmountColumnValidator',
                        severity='CRITICAL',
                        row_index=row.row_index,
                        column=col,
                        raw_value=val,
                        message=f'Stray character or column bleed detected in numeric field {col}',
                        bbox=row.bboxes.get(col)
                    ))
                    
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
            party_val = str(row.data.get('Party', '')).strip()
            if not party_val:
                continue
            
            # Check for isolated digits at the end OR the beginning
            # e.g., "Interest Charge 1" or "1 Interest Charge"
            if re.search(r'(?:^\d+\s+|\s+\d+$)', party_val):
                issues.append(ValidationIssue(
                    rule='ColumnBleedValidator',
                    severity='CRITICAL',
                    row_index=row.row_index,
                    column='Transaction Details',
                    raw_value=party_val,
                    message='Possible column bleed. Stray number found in transaction details.',
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
