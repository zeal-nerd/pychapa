from typing import Literal

# --------------- Types
Mode = Literal["test", "live"]
Status = Literal["pending", "success"]
Currency = Literal["ETB", "USD"]
HttpMethod = Literal["get", "post"]
SplitType = Literal["flat", "percentage"]


# ---------------- Endpoints
class ChapaURLEndPoint:
    swap = "swap"
    banks = "banks"
    events = "events"
    balances = "balances"
    transfers = "transfers"
    subaccount = "subaccount"
    transactions = "transactions"
    bulk_transfers = "bulk-transfers"
    transfers_verify = "transfers/verify"
    transaction_verify = "transaction/verify"
    transaction_initialize = "transaction/initialize"
