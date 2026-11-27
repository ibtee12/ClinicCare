"""Notification Factory Pattern.

Implements GoF Creational Factory Method pattern with extensible registry.
Encapsulates instantiation of multi-channel notification dispatchers
(In-App, Email, SMS). Adding a new channel requires only a new subclass
and a single registry entry.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Type, Optional


@dataclass
class NotificationDispatchResult:
    """Standardized response from any notification delivery channel."""

    channel: str
    recipient_id: int
    message: str
    success: bool
    delivery_id: str


class BaseNotifier(ABC):
    """Abstract Product interface for notifications."""

    @abstractmethod
    def send(
        self,
        recipient_id: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> NotificationDispatchResult:
        """Deliver notification payload to the recipient."""
        pass


class InAppNotifier(BaseNotifier):
    """Product: In-app notification stored in database for user dashboard."""

    def send(
        self,
        recipient_id: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> NotificationDispatchResult:
        delivery_id = f"INAPP-{uuid.uuid4().hex[:8].upper()}"
        return NotificationDispatchResult(
            channel="in_app",
            recipient_id=recipient_id,
            message=message,
            success=True,
            delivery_id=delivery_id,
        )


class EmailNotifier(BaseNotifier):
    """Product: Simulated SMTP email notification written to outbox queue."""

    def send(
        self,
        recipient_id: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> NotificationDispatchResult:
        meta = meta or {}
        to_email = meta.get("to_email", f"user_{recipient_id}@cliniccare.test")
        delivery_id = f"EMAIL-{uuid.uuid4().hex[:8].upper()}"
        # In a real environment, this sends an SMTP message; here it simulates
        # an outbox record with recipient email verification
        return NotificationDispatchResult(
            channel="email",
            recipient_id=recipient_id,
            message=f"[To: {to_email}] {message}",
            success=True,
            delivery_id=delivery_id,
        )


class SMSNotifier(BaseNotifier):
    """Product: Simulated SMS notification to Bangladeshi mobile numbers."""

    def send(
        self,
        recipient_id: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> NotificationDispatchResult:
        meta = meta or {}
        phone = meta.get("phone", "01700000000")
        delivery_id = f"SMS-{uuid.uuid4().hex[:8].upper()}"
        return NotificationDispatchResult(
            channel="sms",
            recipient_id=recipient_id,
            message=f"[SMS to {phone}]: {message}",
            success=True,
            delivery_id=delivery_id,
        )


class NotificationFactory:
    """Creator: Factory managing registration and creation of Notifiers."""

    _registry: Dict[str, Type[BaseNotifier]] = {
        "in_app": InAppNotifier,
        "inapp": InAppNotifier,
        "email": EmailNotifier,
        "mail": EmailNotifier,
        "sms": SMSNotifier,
        "text": SMSNotifier,
    }

    @classmethod
    def register(cls, channel: str, notifier_cls: Type[BaseNotifier]) -> None:
        """Register a new notification channel without altering factory."""
        cls._registry[channel.strip().lower()] = notifier_cls

    @classmethod
    def create(cls, channel: str) -> BaseNotifier:
        """Instantiate and return the appropriate notifier product."""
        clean_channel = (channel or "").strip().lower()
        notifier_class = cls._registry.get(clean_channel)
        if not notifier_class:
            raise ValueError(
                f"Unsupported notification channel '{channel}'. "
                f"Available channels: {list(cls._registry.keys())}"
            )
        return notifier_class()
