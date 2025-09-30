from pydantic import BaseModel
from datetime import datetime

from typing import Optional
from ..utils import Currency, Mode, Status


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
    currency: Currency
    mode: Mode
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
    currency: Currency
    mode: Mode
    status: Status
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
