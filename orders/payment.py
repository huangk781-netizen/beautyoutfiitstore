from django.conf import settings

from .models import Order


def available_payment_methods():
    """Return payment methods that customers may use for new orders."""
    methods = [
        (Order.PaymentMethod.COD.value, Order.PaymentMethod.COD.label),
    ]
    if settings.ENABLE_BANK_TRANSFER:
        methods.insert(
            0,
            (
                Order.PaymentMethod.BANK_TRANSFER.value,
                Order.PaymentMethod.BANK_TRANSFER.label,
            ),
        )
    return methods


def is_payment_method_available(value):
    return value in {method_value for method_value, _ in available_payment_methods()}
