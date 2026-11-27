"""Doctor and department models."""

from app.extensions import db


class Department(db.Model):
    """Medical department / clinical specialty."""

    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    doctors = db.relationship("DoctorProfile", backref="department", lazy=True)

    def __repr__(self) -> str:
        return f"<Department {self.name}>"


class DoctorProfile(db.Model):
    """Doctor clinical credentials, consultation fee, and bio."""

    __tablename__ = "doctor_profiles"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True
    )
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id"), nullable=True
    )
    qualifications = db.Column(db.String(200), nullable=False)
    fee = db.Column(db.Float, nullable=False, default=500.0)
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    availabilities = db.relationship(
        "Availability",
        backref="doctor",
        lazy=True,
        cascade="all, delete-orphan",
    )
    appointments = db.relationship(
        "Appointment", backref="doctor", lazy=True
    )

    def __repr__(self) -> str:
        return f"<DoctorProfile user_id={self.user_id} fee={self.fee}>"


class Availability(db.Model):
    """Weekly recurring availability slot rule."""

    __tablename__ = "availabilities"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctor_profiles.user_id"), nullable=False
    )
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(10), nullable=False)  # "09:00"
    end_time = db.Column(db.String(10), nullable=False)    # "13:00"
    slot_minutes = db.Column(db.Integer, nullable=False, default=20)

    def __repr__(self) -> str:
        return (
            f"<Availability doc={self.doctor_id} "
            f"w={self.weekday} {self.start_time}-{self.end_time}>"
        )
