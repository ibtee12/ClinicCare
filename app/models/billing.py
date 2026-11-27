"""Billing, Invoice and Payment models."""

from datetime import datetime
from app.extensions import db


class Invoice(db.Model):
    """Consultation fee billing invoice."""

    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False,
        unique=True,
    )
    base_fee = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    discount_name = db.Column(db.String(50), default="No Discount")
    total = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="UNPAID"
    )  # UNPAID, PAID, REFUNDED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship(
        "Payment",
        backref="invoice",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Invoice #{self.id} apt={self.appointment_id} "
            f"total={self.total} {self.status}>"
        )


class Payment(db.Model):
    """Payment transaction record for an invoice."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(
        db.Integer, db.ForeignKey("invoices.id"), nullable=False
    )
    method = db.Column(db.String(30), nullable=False)  # card, wallet, bkash
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="PAID"
    )  # PAID, REFUNDED, FAILED
    transaction_ref = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<Payment #{self.id} inv={self.invoice_id} "
            f"ref={self.transaction_ref}>"
        )
