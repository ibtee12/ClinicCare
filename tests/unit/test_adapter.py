from app.patterns.adapter import (
    CardGatewayAdapter,
    MobileWalletAdapter,
    PaymentResult,
)


def test_card_adapter_success():
    adapter = CardGatewayAdapter()
    result = adapter.process_payment(
        amount=800.0,
        payment_data={
            "card_number": "4111222233334444",
            "exp_month": 12,
            "exp_year": 2028,
            "cvv": "123",
        },
    )
    assert isinstance(result, PaymentResult)
    assert result.success is True
    assert result.transaction_ref.startswith("CARD-TX-")
    assert result.retryable is False


def test_card_adapter_declined():
    adapter = CardGatewayAdapter()
    # Test card number ending in 0000 simulates card declined
    result = adapter.process_payment(
        amount=800.0,
        payment_data={
            "card_number": "4111222233330000",
            "exp_month": 12,
            "exp_year": 2028,
            "cvv": "123",
        },
    )
    assert result.success is False
    assert "Declined" in result.message
    assert result.retryable is False


def test_card_adapter_timeout_retryable():
    adapter = CardGatewayAdapter()
    # Test card ending in 9999 simulates gateway timeout (retryable)
    result = adapter.process_payment(
        amount=800.0,
        payment_data={
            "card_number": "4111222233339999",
            "exp_month": 12,
            "exp_year": 2028,
            "cvv": "123",
        },
    )
    assert result.success is False
    assert "Timeout" in result.message
    assert result.retryable is True


def test_mobile_wallet_adapter_success():
    adapter = MobileWalletAdapter()
    result = adapter.process_payment(
        amount=600.0,
        payment_data={
            "wallet_number": "01711223344",
            "pin": "12345",
        },
    )
    assert result.success is True
    assert result.transaction_ref.startswith("WALLET-TX-")
    assert result.retryable is False


def test_mobile_wallet_adapter_invalid_pin():
    adapter = MobileWalletAdapter()
    result = adapter.process_payment(
        amount=600.0,
        payment_data={
            "wallet_number": "01711223344",
            "pin": "00000",
        },
    )
    assert result.success is False
    assert "Invalid PIN" in result.message
    assert result.retryable is False


def test_mobile_wallet_adapter_network_timeout_retryable():
    adapter = MobileWalletAdapter()
    # Phone ending in 999 simulates network timeout
    result = adapter.process_payment(
        amount=600.0,
        payment_data={
            "wallet_number": "01711223999",
            "pin": "12345",
        },
    )
    assert result.success is False
    assert "Network Timeout" in result.message
    assert result.retryable is True
