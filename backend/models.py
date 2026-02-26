from pydantic import BaseModel
from typing import List, Optional


class AnalyzeTextRequest(BaseModel):
    contract_text: str


class Party(BaseModel):
    party_1: str = ""
    party_2: str = ""
    other_parties: List[str] = []


class ContractDuration(BaseModel):
    start_date: str = ""
    end_date: str = ""
    renewal_terms: str = ""
    auto_renewal: str = "Not Found"


class PaymentTerms(BaseModel):
    amounts: str = ""
    payment_schedule: str = ""
    late_fees: str = ""
    refund_policy: str = ""


class TerminationClauses(BaseModel):
    termination_for_convenience: str = ""
    termination_for_cause: str = ""
    notice_period: str = ""
    exit_conditions: str = ""


class LiabilityAndIndemnity(BaseModel):
    liability_cap: str = ""
    indemnification_clause: str = ""


class RiskFlag(BaseModel):
    category: str = ""
    risk_level: str = ""
    reason: str = ""
    clause_reference: str = ""


class UnusualClause(BaseModel):
    clause: str = ""
    why_it_is_risky: str = ""


class ContractAnalysis(BaseModel):
    plain_english_summary: str = ""
    key_parties: Party = Party()
    contract_duration: ContractDuration = ContractDuration()
    payment_terms: PaymentTerms = PaymentTerms()
    termination_clauses: TerminationClauses = TerminationClauses()
    confidentiality_terms: str = ""
    intellectual_property_terms: str = ""
    liability_and_indemnity: LiabilityAndIndemnity = LiabilityAndIndemnity()
    risk_flags: List[RiskFlag] = []
    unusual_or_risky_clauses: List[UnusualClause] = []


class AnalyzeResponse(BaseModel):
    success: bool
    analysis: Optional[ContractAnalysis] = None
    error: Optional[str] = None
