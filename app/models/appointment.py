"""Appointment scheduling model."""

from datetime import datetime
from app.extensions import db


class Appointment(db.Model):
    """Consultation appointment entity with lifecycle status tracking."""

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctor_profiles.user_id"), nullable=False
    )
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(
        db.String(20), nullable=False, default="PENDING"
    )  # PENDING, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    reason = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)  # Doctor clinical visit notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship(
        "User", backref=db.backref("appointments", lazy=True)
    )
    invoice = db.relationship(
        "Invoice",
        backref="appointment",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment #{self.id} doc={self.doctor_id} "
            f"pat={self.patient_id} status={self.status}>"
        )
