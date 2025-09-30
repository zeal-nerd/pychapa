import httpx


class ChapaError(Exception):
    def __init__(self, msg: str, response: httpx.Response | None = None) -> None:
        super().__init__(msg)

        self.response = response
