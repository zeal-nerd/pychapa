from pydantic import BaseModel
from datetime import datetime

from typing import Optional
from .types import CurrencyLiteral, ModeLiteral, StatusLiteral


# ----------------------- Chapa Client Schemas
class ChapaBalance(BaseModel):
    currency: str
    available_balance: float
    ledger_balance: float


class ChapaSubaccount(BaseModel):
    subaccount_id: str


class ChapaCustomization(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None


class PaymentCheckout(BaseModel):
    checkout_url: str


class PaymentDetail(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    amount: float
    charge: Optional[float] = None
    currency: CurrencyLiteral
    mode: ModeLiteral
    status: str
    method: Optional[str] = None
    type: str
    tx_ref: str
    reference: Optional[str] = None
    meta: Optional[str] = None
    customization: Optional[ChapaCustomization] = None
    created_at: datetime
    updated_at: datetime


class TransferDetail(BaseModel):
    account_name: str
    account_number: str
    mobile: Optional[str] = None
    amount: float
    charge: float
    currency: CurrencyLiteral
    mode: ModeLiteral
    status: StatusLiteral
    bank_code: str
    bank_name: str
    transfer_method: str
    tx_ref: str
    chapa_transfer_id: str
    ip_address: Optional[str] = None
    narration: Optional[str] = None
    cross_party_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BulkTransferQueue(BaseModel):
    id: int
    created_at: datetime


# -------------------- Chapa Webhook Schemas
class TransactionEvent:
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    mobile: Optional[str]
    currency: CurrencyLiteral
    payment_method: str
    amount: float
    charge: float
    event: str
    status: str
    type: str
    mode: ModeLiteral
    tx_ref: str
    reference: str
    customization: ChapaCustomization
    meta: Optional[str]
    created_at: str
    updated_at: str


class TransferEvent:
    account_name: str
    account_number: str
    bank_reference: str
    bank_id: int
    bank_name: str
    amount: float
    currency: CurrencyLiteral
    charge: float
    event: str
    status: str
    type: str
    reference: str
    chapa_reference: str
    created_at: datetime
    updated_at: datetime
