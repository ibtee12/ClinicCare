"""Adapter Pattern for Payment Gateways.

Implements GoF Structural Adapter pattern to unify disparate external payment
SDKs (Card Processor and Mobile Wallet SDKs) behind a standard PaymentGateway
interface with robust error handling and retry semantics.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PaymentResult:
    """Standardized response from any adapted payment gateway."""

    success: bool
    transaction_ref: str
    message: str
    retryable: bool = False


class PaymentGateway(ABC):
    """Target interface required by the ClinicCare billing domain."""

    @abstractmethod
    def process_payment(
        self, amount: float, payment_data: Dict[str, Any]
    ) -> PaymentResult:
        """Process a payment and return a unified PaymentResult."""
        pass


# ----------------------------------------------------------------------
# Incompatible 3rd-Party / Legacy Adaptees
# ----------------------------------------------------------------------


class LegacyCardProcessorSdk:
    """Simulated proprietary Card SDK with distinct charge_card signature."""

    def charge_card(
        self,
        card_num: str,
        month: int,
        year: int,
        cvv: str,
        amount_cents: int,
    ) -> Dict[str, Any]:
        clean_num = (card_num or "").replace(" ", "").replace("-", "")
        if clean_num.endswith("0000"):
            return {
                "status": "DECLINED",
                "code": "CARD_DECLINED_INSUFFICIENT_FUNDS",
                "ref": None,
            }
        if clean_num.endswith("9999"):
            return {
                "status": "TIMEOUT",
                "code": "GATEWAY_TIMEOUT",
                "ref": None,
            }
        return {
            "status": "APPROVED",
            "charge_id": f"CARD-TX-{uuid.uuid4().hex[:10].upper()}",
            "amount_charged": amount_cents,
        }


class LegacyMobileWalletSdk:
    """Simulated bKash/Nagad SDK returning tuple (success, tx_id, error)."""

    def transact(
        self,
        msisdn: str,
        amount_bdt: float,
        pin: str,
    ) -> tuple[bool, str, str]:
        if pin == "00000":
            return False, "", "INVALID_PIN"
        if msisdn.endswith("999"):
            return False, "", "NETWORK_TIMEOUT"
        return True, f"WALLET-TX-{uuid.uuid4().hex[:10].upper()}", ""


# ----------------------------------------------------------------------
# Gateway Adapters
# ----------------------------------------------------------------------


class CardGatewayAdapter(PaymentGateway):
    """Adapts LegacyCardProcessorSdk to PaymentGateway."""

    def __init__(self, sdk: LegacyCardProcessorSdk | None = None):
        self._sdk = sdk or LegacyCardProcessorSdk()

    def process_payment(
        self, amount: float, payment_data: Dict[str, Any]
    ) -> PaymentResult:
        cents = int(round(amount * 100))
        resp = self._sdk.charge_card(
            card_num=payment_data.get("card_number", ""),
            month=int(payment_data.get("exp_month", 0)),
            year=int(payment_data.get("exp_year", 0)),
            cvv=payment_data.get("cvv", ""),
            amount_cents=cents,
        )

        status = resp.get("status")
        if status == "APPROVED":
            return PaymentResult(
                success=True,
                transaction_ref=resp.get("charge_id", ""),
                message="Card charge approved successfully.",
                retryable=False,
            )
        elif status == "TIMEOUT":
            return PaymentResult(
                success=False,
                transaction_ref="",
                message="Payment Gateway Timeout. Please retry shortly.",
                retryable=True,
            )
        else:
            return PaymentResult(
                success=False,
                transaction_ref="",
                message=(
                    "Card Declined: Insufficient funds or invalid details."
                ),
                retryable=False,
            )


class MobileWalletAdapter(PaymentGateway):
    """Adapts LegacyMobileWalletSdk (bKash/Nagad) to PaymentGateway."""

    def __init__(self, sdk: LegacyMobileWalletSdk | None = None):
        self._sdk = sdk or LegacyMobileWalletSdk()

    def process_payment(
        self, amount: float, payment_data: Dict[str, Any]
    ) -> PaymentResult:
        msisdn = str(payment_data.get("wallet_number", "")).strip()
        pin = str(payment_data.get("pin", "")).strip()

        success, tx_ref, err = self._sdk.transact(
            msisdn=msisdn, amount_bdt=amount, pin=pin
        )

        if success:
            return PaymentResult(
                success=True,
                transaction_ref=tx_ref,
                message="Mobile wallet transaction confirmed.",
                retryable=False,
            )
        elif err == "NETWORK_TIMEOUT":
            return PaymentResult(
                success=False,
                transaction_ref="",
                message="Network Timeout contacting mobile operator.",
                retryable=True,
            )
        elif err == "INVALID_PIN":
            return PaymentResult(
                success=False,
                transaction_ref="",
                message="Invalid PIN entered for mobile wallet.",
                retryable=False,
            )
        else:
            return PaymentResult(
                success=False,
                transaction_ref="",
                message=f"Mobile wallet payment failed: {err}.",
                retryable=False,
            )


def get_payment_adapter(method: str) -> PaymentGateway:
    """Registry returning configured adapter by method name."""
    clean_method = (method or "").strip().lower()
    if clean_method in ("card", "credit_card", "debit_card"):
        return CardGatewayAdapter()
    elif clean_method in ("wallet", "bkash", "nagad", "mobile_wallet"):
        return MobileWalletAdapter()
    raise ValueError(f"Unsupported payment method: {method}")
