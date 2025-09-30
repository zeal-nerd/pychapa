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
    """
    Synchronous client for interacting with the Chapa payment API.

    This client provides methods for payment processing, transfers, subaccounts,
    and other Chapa API functionality using synchronous HTTP requests.
    """

    def __init__(self, token: str, base_url: str = "https://api.chapa.co/v1") -> None:
        """
        Initialize the Chapa client.

        Args:
            token (str): Your Chapa API token for authentication
            base_url (str, optional): The base URL for the Chapa API.
                Defaults to "https://api.chapa.co/v1"
        """
        logger.info("Initializing Chapa client with base URL: %s", base_url)
        self.__token__ = token
        self.__base_url__ = base_url
        self.__client__ = httpx.Client()

        self.__base_headers__ = {
            "Authorization": f"Bearer {self.__token__}",
            "Content-Type": "application/json",
        }
        logger.debug("Chapa client initialized successfully")

    def _send_request(
        self, method: HttpMethod, path: str, *args, **kwargs
    ) -> httpx.Response:
        """
        Send all requests from a single point with authorization keys.

        Args:
            method (HttpMethod): The HTTP method to use
            path (str): The API endpoint path
            *args: Additional positional arguments for the HTTP request
            **kwargs: Additional keyword arguments for the HTTP request

        Returns:
            httpx.Response: The HTTP response object

        Raises:
            ValueError: If the HTTP method is not valid for httpx.Client
            TypeError: If headers in kwargs is not a valid dict
        """
        logger.debug("Sending %s request to path: %s", method.upper(), path)

        if not hasattr(self.__client__, method):
            logger.error("Invalid HTTP method '%s' for httpx.Client", method)
            raise ValueError(
                f"HTTP method '{method}' is not valid method for httpx.Client"
            )

        headers = {**self.__base_headers__}

        if "headers" in kwargs:
            extra_headers = kwargs["headers"]

            if not isinstance(extra_headers, dict):
                logger.error("Invalid headers type provided, must be dict")
                raise TypeError("headers must be a valid dict")

            headers.update(extra_headers)
            logger.debug("Added extra headers: %s", list(extra_headers.keys()))

        method_effector = getattr(self.__client__, method)
        url = f"{self.__base_url__}/{path.lstrip('/')}"

        try:
            logger.debug("Making HTTP request to: %s", url)
            response = method_effector(url, headers=headers, *args, **kwargs)
            logger.debug("Response status: %s", response.status_code)
            return response
        except Exception as e:
            logger.error("HTTP request failed: %s", str(e))
            raise

    def _check_response(self, response: httpx.Response, data: dict):
        """
        Check non 2xx response status codes and raise exceptions with error details.

        Args:
            response (httpx.Response): The HTTP response object
            data (dict): Response data containing error message

        Raises:
            ChapaError: If the response status indicates an error
        """
        if not response.is_success:
            error_msg = data.get("message", "Unknown error")
            logger.error(
                "API request failed with status %s: %s", response.status_code, error_msg
            )
            raise ChapaError(error_msg, response)

    def _extract_json_data(self, response: httpx.Response) -> dict:
        """
        Extract JSON body and serialize it to Python dict objects.

        Args:
            response (httpx.Response): The HTTP response object

        Returns:
            dict: The parsed JSON response data

        Raises:
            ChapaError: If the response contains invalid JSON or indicates an error
        """
        try:
            data = response.json()
        except httpx.DecodingError:
            raise ChapaError("Invalid JSON response", response)

        self._check_response(response, data)
        return data

    def _check_data_fields(self, data: dict, fields: list[str]):
        """
        Check if response data includes required fields and raise if one is missing.

        Args:
            data (dict): The response data to validate
            fields (list[str]): List of required field names

        Raises:
            ChapaError: If any required field is missing from the data
        """
        for field in fields:
            if field not in data:
                logger.error("Missing required field '%s' in response data", field)
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
        Initialize a payment transaction.

        Args:
            amount (int | float): The amount to be charged
            currency (str, optional): The currency for the payment
            first_name (str, optional): Customer's first name
            last_name (str, optional): Customer's last name
            phone_number (str, optional): Customer's phone number
            email (str, optional): Customer's email address
            callback_url (str, optional): URL to redirect after payment
            return_url (str, optional): URL to return to after payment
            customization (dict, optional): Payment form customization options
            subaccount_id (str, optional): ID of the subaccount to use
            tx_ref (str, optional): Unique transaction reference
            meta (dict, optional): Additional metadata for the transaction

        Returns:
            PaymentCheckout: Object containing checkout URL and other payment details
        """
        logger.info("Initializing payment for amount: %s", amount)

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

        logger.info("Payment initialized successfully with checkout URL")
        return PaymentCheckout(**data)

    def verify_transaction(self, tx_ref: str) -> PaymentDetail:
        """
        Verify a payment transaction.

        Args:
            tx_ref (str): The transaction reference to verify

        Returns:
            PaymentDetail: Object containing detailed payment information
        """
        logger.info("Verifying transaction with reference: %s", tx_ref)

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
        Create a subaccount for payment splitting.

        Args:
            account_name (str): The name of the account holder
            bank_code (int): The bank code for the account
            account_number (str): The account number
            split_value (int | float): The value to split (amount or percentage)
            split_type (SplitType): The type of split (percentage or flat)
            business_name (str, optional): The name of the business

        Returns:
            ChapaSubaccount: Object containing subaccount details including subaccount_id
        """
        logger.info("Creating subaccount for account: %s", account_name)

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
        """
        Get a paginated list of transactions.

        Args:
            page (int, optional): The page number to retrieve. Defaults to 1
            per_page (int, optional): Number of transactions per page. Defaults to 10

        Returns:
            dict: Dictionary containing paginated transaction data
        """
        logger.debug("Fetching transactions - page: %s, per_page: %s", page, per_page)
        params = {"page": page, "per_page": per_page}

        response = self._send_request(
            "get", ChapaURLEndPoint.transactions, params=params
        )
        json_data = self._extract_json_data(response)

        return json_data.get("data", {})

    def get_transaction_log(self, tx_ref: str) -> list:
        """
        Get the transaction log for a specific transaction.

        Args:
            tx_ref (str): The transaction reference to get logs for

        Returns:
            list: List of transaction log entries
        """
        logger.debug("Fetching transaction log for reference: %s", tx_ref)
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
        """
        Initialize a bank transfer.

        Args:
            amount (int): The amount to transfer
            account_number (str): The destination account number
            bank_code (int): The bank code for the destination bank
            currency (str, optional): The currency for the transfer
            account_name (str, optional): The name of the account holder
            reference (str, optional): Unique reference for the transfer

        Returns:
            str | None: Transfer data
        """
        logger.info(
            "Initializing transfer for amount: %s to account: %s",
            amount,
            account_number,
        )
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
        """
        Initialize bulk transfers.

        Args:
            title (str, optional): Title for the bulk transfer
            currency (Currency, optional): Currency for the transfers
            bulk_data (list[dict]): List of transfer data dictionaries

        Returns:
            BulkTransferQueue: Object containing bulk transfer queue information
        """
        logger.info("Initializing bulk transfer with %s transfers", len(bulk_data))
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
        """
        Verify a transfer transaction.

        Args:
            tx_ref (str): The transfer reference to verify

        Returns:
            TransferDetail: Object containing detailed transfer information
        """
        logger.info("Verifying transfer with reference: %s", tx_ref)
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
        """
        Get a paginated list of transfers.

        Args:
            page (int, optional): The page number to retrieve. Defaults to 1
            per_page (int, optional): Number of transfers per page. Defaults to 10

        Returns:
            dict: Dictionary containing paginated transfer data
        """
        logger.debug("Fetching transfers - page: %s, per_page: %s", page, per_page)
        params = {"page": page, "per_page": per_page}
        response = self._send_request("get", ChapaURLEndPoint.transfers, params=params)
        json_data = self._extract_json_data(response)

        return json_data.get("data", {})

    def banks(self) -> dict:
        """
        Get a list of supported banks.

        Returns:
            dict: Dictionary containing list of available banks
        """
        logger.debug("Fetching list of supported banks")
        response = self._send_request("get", ChapaURLEndPoint.banks)
        json_data = self._extract_json_data(response)

        return json_data

    def balances(self, currency: Currency | None = None) -> list:
        """
        Get available balances.

        Args:
            currency (Currency, optional): Specific currency to get balance for

        Returns:
            list: List of ChapaBalance objects containing balance information
        """
        logger.debug(
            "Fetching balances for currency: %s",
            currency if currency else "all currencies",
        )
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
        """
        Swap currency between different supported currencies.

        Args:
            amount (int | float): The amount to swap
            from_currency (Currency): The source currency to swap from
            to_currency (Currency): The target currency to swap to

        Returns:
            dict: Dictionary containing swap transaction details
        """
        logger.info(
            "Initiating currency swap: %s %s to %s", amount, from_currency, to_currency
        )
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
        logger.debug("Closing Chapa HTTP client")
        self.__client__.close()
