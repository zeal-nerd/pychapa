import httpx
import logging
from .schema import (
    BulkTransferQueue,
    ChapaBalance,
    ChapaSubaccount,
    PaymentCheckout,
    PaymentDetail,
    TransferDetail,
)
from ..utils import HttpMethod, Currency, SplitType, ChapaURLEndPoint
from ..exception import ChapaError

logger = logging.getLogger("pychapa")


class Chapa:
    def __init__(self, token: str, base_url: str = "https://api.chapa.co/v1") -> None:
        self.__token__ = token
        self.__base_url__ = base_url
        self.__client__ = httpx.Client()

        self.__base_headers__ = {
            "Authorization": f"Bearer {self.__token__}",
            "Content-Type": "application/json",
        }

    def _send_request(
        self, method: HttpMethod, path: str, *args, **kwargs
    ) -> httpx.Response:
        """Sending all requests from a single point with authorization keys"""
        if not hasattr(self.__client__, method):
            raise ValueError(
                f"HTTP method '{method}' is not valid method for httpx.Client"
            )

        headers = {**self.__base_headers__}

        if "headers" in kwargs:
            extra_headers = kwargs["headers"]

            if not isinstance(extra_headers, dict):
                raise TypeError("headers must be a valid dict")

            headers.update(extra_headers)

        method_effector = getattr(self.__client__, method)
        url = f"{self.__base_url__}/{path.lstrip('/')}"
        response = method_effector(url, headers=headers, *args, **kwargs)
        return response

    def _check_response(self, response: httpx.Response, data: dict):
        """Checking non 2xx response status codes and raising exceptions with error details"""
        if not response.is_success:
            raise ChapaError(data.get("message", "Unknown error"), response)

    def _extract_json_data(self, response: httpx.Response) -> dict:
        """Extracting json body and serilizing them to python dict objects"""
        try:
            data = response.json()
        except httpx.DecodingError:
            raise ChapaError("Invalid JSON response", response)

        self._check_response(response, data)
        return data

    def _check_data_fields(self, data: dict, fields: list[str]):
        """Checking if a response data includes required fields and raising if one is missing"""
        for field in fields:
            if field not in data:
                raise ChapaError(f"data missing {field} field")

    def init_payment(
        self,
        amount: int | float,
        currency: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
        callback_url: str | None = None,
        return_url: str | None = None,
        customization: dict | None = None,
        subaccount_id: str | None = None,
        tx_ref: str | None = None,
        meta: dict | None = None,
    ) -> PaymentCheckout:
        """
        Initializes a payment
        Args:
            amount (int): The amount to be charged
            currency (str):

        Returns:
            (dict): A dictionary containing checkout url

        """

        path = "/transaction/initialize"
        payload: dict = {"amount": str(amount)}

        if currency:
            payload["currency"] = currency

        if first_name:
            payload["first_name"] = first_name

        if last_name:
            payload["last_name"] = last_name

        if phone_number:
            payload["phone_number"] = phone_number

        if email:
            payload["email"] = email

        if callback_url:
            payload["callback_url"] = callback_url

        if return_url:
            payload["return_url"] = return_url

        if tx_ref:
            payload["tx_ref"] = tx_ref

        if customization:
            payload["customization"] = customization

        if subaccount_id:
            payload["subaccount_id"] = subaccount_id

        if meta:
            payload["meta"] = meta

        response = self._send_request("post", path, json=payload)

        json_data = self._extract_json_data(response)
        data = json_data.get("data", {})
        self._check_data_fields(data, ["checkout_url"])

        return PaymentCheckout(**data)

    def verify_transaction(self, tx_ref: str) -> PaymentDetail:
        """Verifing transactions"""

        path = f"/transaction/verify/{tx_ref}"

        response = self._send_request("get", path)
        json_data = self._extract_json_data(response)
        data = json_data.get("data", {})
        self._check_data_fields(
            data,
            [
                "first_name",
                "last_name",
                "email",
                "amount",
                "charge",
                "currency",
                "mode",
                "status",
                "method",
                "type",
                "tx_ref",
                "reference",
                "created_at",
                "updated_at",
            ],
        )
        return PaymentDetail(**data)

    def create_subaccount(
        self,
        account_name: str,
        bank_code: int,
        account_number: str,
        split_value: int | float,
        split_type: SplitType,
        business_name: str | None = None,
    ) -> ChapaSubaccount:
        """
        Creates a subaccount.

        Args:
            amount (int): The amount to be charged
            currency (str):

        Returns:
            dict: containing subaccount_id
        """

        path = "/subaccount"

        payload = {
            "account_name": account_name,
            "bank_code": bank_code,
            "account_number": account_number,
            "split_value": split_value,
            "split_type": split_type,
        }

        if business_name:
            payload["business_name"] = business_name

        response = self._send_request("post", path, json=payload)
        json_data = self._extract_json_data(response)

        data = json_data.get("data", {})
        self._check_data_fields(data, ["subaccount_id"])

        return ChapaSubaccount(**data)

    def get_transactions(self, page: int = 1, per_page: int = 10) -> dict:
        """Fetching paginated list of transactions made"""
        params = {"page": page, "per_page": per_page}

        response = self._send_request(
            "get", ChapaURLEndPoint.transactions, params=params
        )
        json_data = self._extract_json_data(response)

        return json_data.get("data", {})

    def get_transaction_log(self, tx_ref: str) -> list:
        """Fetching a transaction log"""
        path = f"{ChapaURLEndPoint.events}/{tx_ref}"
        response = self._send_request("get", path)
        json_data = self._extract_json_data(response)

        return json_data.get("data", [])

    def init_transfer(
        self,
        amount: int,
        account_number: str,
        bank_code: int,
        currency: str | None = None,
        account_name: str | None = None,
        reference: str | None = None,
    ) -> str | None:
        """Initializing bank transfers"""
        payload = {
            "account_number": account_number,
            "amount": amount,
            "bank_code": bank_code,
        }

        if currency:
            payload["currency"] = currency

        if account_name:
            payload["account_name"] = account_name

        if reference:
            payload["reference"] = reference

        response = self._send_request("post", ChapaURLEndPoint.transfers, json=payload)
        json_data = self._extract_json_data(response)

        return json_data.get("data")

    def bulk_transfer(
        self,
        title: str | None,
        currency: Currency | None,
        bulk_data: list[dict],
    ) -> BulkTransferQueue:
        """Init bulk transfers"""
        payload = {}

        if title:
            payload["title"] = title

        if currency:
            payload["currency"] = currency

        payload.update({"bulk_data": bulk_data})

        response = self._send_request(
            "post", ChapaURLEndPoint.bulk_transfers, json=payload
        )
        json_data = self._extract_json_data(response)
        data = json_data.get("data", {})
        self._check_data_fields(data, ["id", "created_at"])
        return BulkTransferQueue(**data)

    def verify_transfer(self, tx_ref: str) -> TransferDetail:
        """Verify transfer"""
        path = f"{ChapaURLEndPoint.transfers_verify}/{tx_ref}"

        response = self._send_request("get", path)
        json_data = self._extract_json_data(response)
        data = json_data.get("data", {})
        self._check_data_fields(
            data,
            [
                "account_name",
                "account_number",
                "amount",
                "charge",
                "currency",
                "mode",
                "status",
                "bank_code",
                "bank_name",
                "transfer_method",
                "tx_ref",
                "chapa_transfer_id",
                "created_at",
                "updated_at",
            ],
        )
        return TransferDetail(**data)

    def get_transfers(self, page: int = 1, per_page: int = 10) -> dict:
        """Get paginated list of transfers"""
        params = {"page": page, "per_page": per_page}
        response = self._send_request("get", ChapaURLEndPoint.transfers, params=params)
        json_data = self._extract_json_data(response)

        return json_data.get("data", {})

    def banks(self) -> dict:
        """Get a list of banks"""
        response = self._send_request("get", ChapaURLEndPoint.banks)
        json_data = self._extract_json_data(response)

        return json_data

    def balances(self, currency: Currency | None = None) -> list:
        """Get available balances"""
        path = ChapaURLEndPoint.balances

        if currency:
            path = f"{path}/{currency.lower()}"

        response = self._send_request("get", path)
        json_data = self._extract_json_data(response)

        balances = json_data.get("data", [])
        data = []
        for balance in balances:
            self._check_data_fields(
                balance,
                [
                    "currency",
                    "available_balance",
                    "ledger_balance",
                ],
            )
            data.append(ChapaBalance(**balance))

        return data

    def swap(
        self, amount: int | float, from_currency: Currency, to_currency: Currency
    ) -> dict:
        """Swap currency"""
        payload = {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
        }

        response = self._send_request("post", ChapaURLEndPoint.swap, json=payload)
        json_data = self._extract_json_data(response)

        return json_data.get("data", {})

    def close(self) -> None:
        """Close http client"""
        self.__client__.close()
