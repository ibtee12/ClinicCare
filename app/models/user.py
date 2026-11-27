"""User model for ClinicCare authentication and role authorization."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """Core user entity representing Patients, Doctors, and Admins."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.String(20), nullable=False, default="patient"
    )  # patient, doctor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient_profile = db.relationship(
        "PatientProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    doctor_profile = db.relationship(
        "DoctorProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify plain password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
