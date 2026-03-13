from typing import NamedTuple

from env import Env


class FlowExtensionCredential(NamedTuple):
    flow_extension_id: str
    http_basic_token: str
    api_key: str


INVOICE_FLOW_EXTENSION_CREDENTIAL = FlowExtensionCredential(
    flow_extension_id=Env.str("INVOICE_FLOW_EXTENSION_ID"),  # type: ignore
    http_basic_token=Env.str("INVOICE_FLOW_EXTENSION_TOKEN"),  # type: ignore
    api_key=Env.str("INVOICE_FLOW_EXTENSION_API_KEY"),  # type: ignore
)
