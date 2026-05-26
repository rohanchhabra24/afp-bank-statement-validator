from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ValidationIssue(BaseModel):
    rule: str
    severity: str  # CRITICAL, WARNING, INFO
    row_index: int
    column: str
    raw_value: str
    message: str
    bbox: Optional[List[float]] = None # [x0, y0, x1, y1] for highlighting

class TransactionRow(BaseModel):
    row_index: int
    data: Dict[str, Any]
    bboxes: Dict[str, List[float]] # column name -> bbox

class ValidationResult(BaseModel):
    issues: List[ValidationIssue]
    summary: Dict[str, Any]
