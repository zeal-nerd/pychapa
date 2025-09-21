from secrets import token_urlsafe


def generate_txref():
    return token_urlsafe(12)
