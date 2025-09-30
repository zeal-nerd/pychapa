import logging
import secrets

from pprint import pprint as pp
from src.pychapa import Chapa

CHAPA_API_TOKEN = "CHASECK_TEST-Some_Test_Token"
chapa = Chapa(token=CHAPA_API_TOKEN)

tx_ref = secrets.token_urlsafe()

logging.basicConfig(level="INFO")


def test_init_payment():
    data = chapa.init_payment(
        amount=100,
        tx_ref=tx_ref,
    )
    pp(data)


def test_verify_payment():
    data = chapa.verify_transaction(tx_ref=tx_ref)
    pp(data)


def test_get_transaction():
    data = chapa.get_transactions()
    pp(data)


def test_get_transfers():
    data = chapa.get_transfers()
    pp(data)


def test_get_balances():
    data = chapa.balances()
    pp(data)


def test_init_transfer():
    data = chapa.init_transfer(200, "0900123456", 855)
    pp(data)


# test_init_payment()
# test_verify_payment()
# test_get_balances()
# test_init_transfer()
