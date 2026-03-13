from django.contrib import admin

from app.solutions.ship_to_detection.models import ValidShipToAddress


@admin.register(ValidShipToAddress)
class ValidShipToAddressAdmin(admin.ModelAdmin[ValidShipToAddress]):
    list_display = [
        "name",
        "street",
        "city",
        "state",
        "country",
        "postal_code",
    ]
