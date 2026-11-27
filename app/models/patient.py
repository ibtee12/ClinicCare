"""Patient profile and medical record models."""

from app.extensions import db


class PatientProfile(db.Model):
    """Profile details specific to patients."""

    __tablename__ = "patient_profiles"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True
    )
    age = db.Column(db.Integer, default=30)
    gender = db.Column(db.String(20), default="Other")  # Male, Female, Other
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)  # A+, B+, O+, AB+
    is_student = db.Column(db.Boolean, default=False)
    medical_history = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PatientProfile user_id={self.user_id}>"
