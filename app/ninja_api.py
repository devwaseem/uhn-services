from ninja import NinjaAPI

from app.solutions.contract_workspaces.api import (
    router as contract_workspaces_router,
)
from app.solutions.non_po_invoices.api import router as non_po_invoices_router

api = NinjaAPI()
api.add_router("/non-po-invoices/", non_po_invoices_router)
api.add_router("/contract-workspaces/", contract_workspaces_router)
