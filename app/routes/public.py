"""Public browsing routes: landing, doctor directory, doctor profile."""

from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, abort
from app.models.doctor import Department, DoctorProfile
from app.services.slot_service import get_available_slots

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    """Clinic homepage with hero, specialties, and featured doctors."""
    departments = Department.query.limit(6).all()
    featured_doctors = (
        DoctorProfile.query.filter_by(is_active=True).limit(4).all()
    )
    return render_template(
        "public/index.html",
        departments=departments,
        featured_doctors=featured_doctors,
    )


@public_bp.route("/doctors")
def doctors():
    """Search and filter doctors directory by department and doctor name."""
    dept_name = request.args.get("department", "").strip()
    query_str = request.args.get("q", "").strip()

    query = DoctorProfile.query.filter_by(is_active=True)

    if dept_name:
        dept = Department.query.filter_by(name=dept_name).first()
        if dept:
            query = query.filter(DoctorProfile.department_id == dept.id)

    doctor_list = query.all()

    if query_str:
        doctor_list = [
            doc
            for doc in doctor_list
            if query_str.lower() in doc.user.name.lower()
            or (doc.bio and query_str.lower() in doc.bio.lower())
        ]

    departments = Department.query.all()
    return render_template(
        "public/doctors.html",
        doctors=doctor_list,
        departments=departments,
        selected_dept=dept_name,
        search_query=query_str,
    )


@public_bp.route("/doctors/<int:doctor_id>")
def doctor_detail(doctor_id: int):
    """Doctor profile view with interactive slot picker."""
    doctor = DoctorProfile.query.filter_by(
        user_id=doctor_id, is_active=True
    ).first()
    if not doctor:
        abort(404)

    # Date selection (default: tomorrow, max 60 days)
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today() + timedelta(days=1)
    else:
        target_date = date.today() + timedelta(days=1)

    slots = get_available_slots(doctor_id, target_date)

    return render_template(
        "public/doctor_detail.html",
        doctor=doctor,
        target_date=target_date,
        slots=slots,
    )
