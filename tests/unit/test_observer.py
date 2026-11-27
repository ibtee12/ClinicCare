from app.patterns.observer import (
    AppointmentEvent,
    AppointmentSubject,
    NotificationObserver,
    InvoiceObserver,
    AuditLogObserver,
)


def test_observer_attachment_and_notification():
    subject = AppointmentSubject()
    notify_obs = NotificationObserver()
    invoice_obs = InvoiceObserver()
    audit_obs = AuditLogObserver()

    subject.attach(notify_obs)
    subject.attach(invoice_obs)
    subject.attach(audit_obs)

    event = AppointmentEvent(
        event_type="CANCELLED",
        appointment_id=101,
        patient_id=5,
        doctor_id=2,
        payload={"hours_before": 26, "fee": 800.0, "paid": True},
    )

    subject.notify(event)

    # Verify NotificationObserver reacted
    notifications = notify_obs.get_dispatched()
    assert len(notifications) == 1
    assert notifications[0]["recipient_id"] == 5
    assert "cancelled" in notifications[0]["message"].lower()

    # Verify InvoiceObserver processed refund calculation
    refunds = invoice_obs.get_refund_events()
    assert len(refunds) == 1
    assert refunds[0]["refund_amount"] == 800.0  # 100% refund for >=24 hours
    assert refunds[0]["refund_status"] == "FULL_REFUND"

    # Verify AuditLogObserver recorded the audit trail
    logs = audit_obs.get_logs()
    assert len(logs) == 1
    assert logs[0]["event_type"] == "CANCELLED"
    assert logs[0]["appointment_id"] == 101


def test_invoice_observer_partial_refund():
    subject = AppointmentSubject()
    invoice_obs = InvoiceObserver()
    subject.attach(invoice_obs)

    # Cancelled between 2 and 24 hours (e.g. 10 hours) -> 50% refund
    event = AppointmentEvent(
        event_type="CANCELLED",
        appointment_id=102,
        patient_id=6,
        doctor_id=3,
        payload={"hours_before": 10, "fee": 600.0, "paid": True},
    )
    subject.notify(event)

    refunds = invoice_obs.get_refund_events()
    assert len(refunds) == 1
    assert refunds[0]["refund_amount"] == 300.0
    assert refunds[0]["refund_status"] == "PARTIAL_REFUND"


def test_observer_detach():
    subject = AppointmentSubject()
    audit_obs = AuditLogObserver()
    subject.attach(audit_obs)
    subject.detach(audit_obs)

    event = AppointmentEvent(
        event_type="CONFIRMED",
        appointment_id=103,
        patient_id=7,
        doctor_id=4,
    )
    subject.notify(event)
    assert len(audit_obs.get_logs()) == 0
