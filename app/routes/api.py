"""REST API endpoints under /api/v1."""

from datetime import datetime, date
from flask import Blueprint, jsonify, request
from app.models.doctor import DoctorProfile
from app.models.appointment import Appointment
from app.services.slot_service import get_available_slots

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/doctors", methods=["GET"])
def get_doctors():
    """JSON list of all active doctors."""
    doctors = DoctorProfile.query.filter_by(is_active=True).all()
    data = [
        {
            "id": doc.user_id,
            "name": doc.user.name,
            "department": doc.department.name if doc.department else "General",
            "qualifications": doc.qualifications,
            "fee": doc.fee,
            "bio": doc.bio,
        }
        for doc in doctors
    ]
    return jsonify(data)


@api_bp.route("/doctors/<int:doctor_id>/slots", methods=["GET"])
def get_doctor_slots(doctor_id: int):
    """JSON list of discrete slots for a target date."""
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    slots = get_available_slots(doctor_id, target_date)
    return jsonify(
        [
            {
                "time": s["time_str"],
                "display": s["display_time"],
                "datetime": s["datetime"].isoformat(),
                "is_booked": s["is_booked"],
            }
            for s in slots
        ]
    )


@api_bp.route("/appointments", methods=["GET"])
def get_appointments():
    """JSON list of recent appointments."""
    appointments = (
        Appointment.query.order_by(Appointment.start_datetime.desc())
        .limit(20)
        .all()
    )
    return jsonify(
        [
            {
                "id": a.id,
                "patient": a.patient.name,
                "doctor": a.doctor.user.name,
                "start_time": a.start_datetime.isoformat(),
                "status": a.status,
                "fee": a.invoice.total if a.invoice else None,
            }
            for a in appointments
        ]
    )
