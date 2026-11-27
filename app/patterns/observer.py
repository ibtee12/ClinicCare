"""Observer Pattern for Appointment Lifecycle Events.

Implements GoF Behavioral Observer pattern. When an appointment transitions
between statuses (CREATED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW),
attached observers react independently to dispatch notifications, adjust
invoices/refunds, and maintain audit trail logs without coupling the domain.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class AppointmentEvent:
    """Encapsulates appointment lifecycle event details."""

    event_type: str  # CREATED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    appointment_id: int
    patient_id: int
    doctor_id: int
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AppointmentObserver(ABC):
    """Abstract Observer interface."""

    @abstractmethod
    def update(self, event: AppointmentEvent) -> None:
        """Receive appointment lifecycle update."""
        pass


class NotificationObserver(AppointmentObserver):
    """Dispatches in-app, SMS, and email alerts on appointment changes."""

    def __init__(self):
        self._dispatched: List[Dict[str, Any]] = []

    def update(self, event: AppointmentEvent) -> None:
        message = ""
        if event.event_type == "CANCELLED":
            message = (
                f"Appointment #{event.appointment_id} cancelled."
            )
        elif event.event_type == "CONFIRMED":
            message = (
                f"Appointment #{event.appointment_id} confirmed."
            )
        elif event.event_type == "COMPLETED":
            message = (
                f"Appointment #{event.appointment_id} completed."
            )
        else:
            message = (
                f"Appointment #{event.appointment_id} updated: "
                f"{event.event_type}."
            )

        record = {
            "recipient_id": event.patient_id,
            "message": message,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
        }
        self._dispatched.append(record)

    def get_dispatched(self) -> List[Dict[str, Any]]:
        return self._dispatched


class InvoiceObserver(AppointmentObserver):
    """Adjusts billing invoices and computes refunds on cancellation."""

    def __init__(self):
        self._refund_events: List[Dict[str, Any]] = []

    def update(self, event: AppointmentEvent) -> None:
        if event.event_type == "CANCELLED":
            payload = event.payload
            fee = float(payload.get("fee", 0.0))
            hours_before = float(payload.get("hours_before", 0.0))
            is_paid = bool(payload.get("paid", False))

            if is_paid and fee > 0:
                if hours_before >= 24.0:
                    refund_amount = fee
                    status = "FULL_REFUND"
                elif hours_before >= 2.0:
                    refund_amount = round(fee * 0.50, 2)
                    status = "PARTIAL_REFUND"
                else:
                    refund_amount = 0.0
                    status = "NO_REFUND"

                self._refund_events.append(
                    {
                        "appointment_id": event.appointment_id,
                        "refund_amount": refund_amount,
                        "refund_status": status,
                        "hours_before": hours_before,
                    }
                )

    def get_refund_events(self) -> List[Dict[str, Any]]:
        return self._refund_events


class AuditLogObserver(AppointmentObserver):
    """Maintains an append-only audit trail for compliance and reporting."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def update(self, event: AppointmentEvent) -> None:
        log_entry = {
            "appointment_id": event.appointment_id,
            "event_type": event.event_type,
            "patient_id": event.patient_id,
            "doctor_id": event.doctor_id,
            "timestamp": event.timestamp,
            "details": event.payload,
        }
        self._logs.append(log_entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        return self._logs


class AppointmentSubject:
    """Subject managing appointment event subscribers."""

    def __init__(self):
        self._observers: List[AppointmentObserver] = []

    def attach(self, observer: AppointmentObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: AppointmentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: AppointmentEvent) -> None:
        for observer in list(self._observers):
            observer.update(event)


# Global default subject singleton instance for app-wide event dispatch
_default_subject: Optional[AppointmentSubject] = None


def get_appointment_subject() -> AppointmentSubject:
    """Return configured global AppointmentSubject."""
    global _default_subject
    if _default_subject is None:
        _default_subject = AppointmentSubject()
    return _default_subject
