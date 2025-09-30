import json
import logging
from typing import Literal

import httpx

"""
Asynchronous Chapa Client
"""

logger = logging.getLogger(__name__)


class Chapa:

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.chapa.co/v1",
    ) -> None:
        """
        Initilize chapa client instance.

        Args:
                        token (str) : Chapa's API Token.
                        **defaults : Default to always include.

        """

        self.secret = token
        self.base_url = base_url
        self.client = httpx.AsyncClient()

        self.headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def extract_fields(response_dict: dict) -> list:
        fields = []

        for key in response_dict:
            fields.append(response_dict[key])

        return fields

    async def send_request(
        self, method: str, path: str, *args, **kwargs
    ) -> httpx.Response:
        """Sends a request to chapa"""
        url = self.base_url + path

        if not hasattr(self.client, method):
            raise Exception(f"Httpx client does not have a {method} method.")

        sender = getattr(self.client, method)
        response = await sender(url, *args, headers=self.headers, **kwargs)
        return response

    async def init_payment(
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
    ) -> str | None:
        """
        Initializes a payment link.

        Args:
                        amount (int): The amount to be charged
                        currency (str):

        Returns:
                        str | None: The checkout url if successful.
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
            payload["customization"] = json.dumps(customization)

        if subaccount_id:
            payload["subaccount_id"] = subaccount_id

        if meta:
            payload["meta"] = json.dumps(meta)

        response = await self.send_request("post", path, json=payload)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)
            if response.is_success:
                # User message and status for logging
                checkout_url = data["checkout_url"]
                logger.info("%s %s %s", status, msg, data)
                return checkout_url

            else:
                logger.error("%s %s  %s %s", response.status_code, status, msg, data)

    async def verify_payment(self, trx_ref: str) -> dict | None:
        path = f"/verify/{trx_ref}"

        response = await self.send_request("get", path)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)

            if response.is_success:
                logger.info("%s %s %s", status, msg, data)
                return data
            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)

    async def get_transactions(self, page: int = 1, per_page: int = 10) -> dict | None:

        path = "/transactions"
        params = {"page": page, "per_page": per_page}

        response = await self.send_request("get", path, params=params)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)

            if response.is_success:
                transactions = data["transactions"]
                logger.info("%s %s", status, msg)
                return transactions

            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)

    async def create_subaccount(
        self,
        account_name: str,
        bank_code: int,
        account_number: str,
        split_value: int | float,
        split_type: Literal["percentage", "flat"],
        business_name: str | None = None,
    ) -> str | None:
        """
        Creates a subaccount.

        Args:
            amount (int): The amount to be charged
            currency (str):

        Returns:
            str | None: The subaccount_id if successful.
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

        response = await self.send_request("post", path, json=payload)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)
            if response.is_success:
                subaccount_id = data["subaccount_id"]
                logger.info("%s %s %s", status, msg, data)
                return subaccount_id

            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)

    async def init_transfer(
        self,
        amount: int,
        account_number: str,
        bank_code: int,
        currency: str | None = None,
        account_name: str | None = None,
        reference: str | None = None,
    ):
        path = "/transfers"

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

        response = await self.send_request("post", path, json=payload)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)

            if response.is_success:
                logger.info("%s %s %s", status, msg, data)
                return True

            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)
                return False

    async def verify_transfer(self, trx_ref: str) -> dict | None:
        path = f"/transfers/verify/{trx_ref}"

        response = await self.send_request("get", path)
        json_response = response.json()

        if json_response:
            msg, status, data = self.extract_fields(json_response)
            if response.is_success:
                logger.info("%s %s", status, msg)
                return data

            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)
                return

    async def get_transfers(self, page: int = 1, per_page: int = 10) -> tuple | None:

        path = "/transfers"

        params = {"page": page, "per_page": per_page}
        response = await self.send_request("get", path, params=params)
        json_response = response.json()

        if json_response:
            msg, status, meta, data = self.extract_fields(json_response)

            if response.is_success:
                logger.info("%s %s", status, msg)
                return meta, data

            else:
                logger.error("%s %s %s %s", response.status_code, status, msg, data)
                return


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    logging.basicConfig(level=logging.DEBUG)

    async def main():
        CHAPA_TOKEN = "CHASECK_TEST-05htznendfNGDLxqZWky057mMfDtjrXK"
        chapa = Chapa(CHAPA_TOKEN)

        # Initializ Payment
        # amount = 30
        # checkout_url = await chapa.init_payment(amount)
        # print(f'Pay {amount}:', checkout_url)

        # await chapa.init_transfer(
        #     amount=100,
        #     bank_code=855,
        #     account_number="0900123456",
        # )

        pprint(await chapa.get_transactions(1000))

    asyncio.run(main())
