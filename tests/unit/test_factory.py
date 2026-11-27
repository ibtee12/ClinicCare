import pytest
from app.patterns.factory import (
    NotificationFactory,
    InAppNotifier,
    EmailNotifier,
    SMSNotifier,
    BaseNotifier,
    NotificationDispatchResult,
)


def test_factory_creates_inapp_notifier():
    notifier = NotificationFactory.create("in_app")
    assert isinstance(notifier, InAppNotifier)
    res = notifier.send(recipient_id=1, message="Welcome to ClinicCare")
    assert isinstance(res, NotificationDispatchResult)
    assert res.channel == "in_app"
    assert res.success is True


def test_factory_creates_email_notifier():
    notifier = NotificationFactory.create("email")
    assert isinstance(notifier, EmailNotifier)
    res = notifier.send(
        recipient_id=2,
        message="Appointment confirmed",
        meta={"to_email": "patient@example.com"},
    )
    assert res.channel == "email"
    assert res.success is True


def test_factory_creates_sms_notifier():
    notifier = NotificationFactory.create("sms")
    assert isinstance(notifier, SMSNotifier)
    res = notifier.send(
        recipient_id=3,
        message="Reminder: Clinic visit today",
        meta={"phone": "01711000000"},
    )
    assert res.channel == "sms"
    assert res.success is True


def test_factory_invalid_channel():
    with pytest.raises(ValueError) as exc:
        NotificationFactory.create("carrier_pigeon")
    assert "Unsupported notification channel" in str(exc.value)


def test_factory_register_new_channel():
    class PushNotifier(BaseNotifier):
        def send(self, recipient_id, message, meta=None):
            return NotificationDispatchResult(
                channel="push",
                recipient_id=recipient_id,
                message=message,
                success=True,
                delivery_id="PUSH-123",
            )

    NotificationFactory.register("push", PushNotifier)
    notifier = NotificationFactory.create("push")
    assert isinstance(notifier, PushNotifier)
    res = notifier.send(recipient_id=4, message="Push notification")
    assert res.channel == "push"
    assert res.delivery_id == "PUSH-123"
