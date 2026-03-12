import httpx


class FlowExtensionAuthFailedError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response


class FlowExtensionEventDataNotFoundError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response


class FlowExtensionRateLimitError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
