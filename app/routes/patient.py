"""Patient management blueprint and routes."""

import re
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from app.extensions import db
from app.routes.auth import role_required, get_current_user
from app.models.patient import PatientProfile
from app.models.appointment import Appointment
from app.models.billing import Invoice
from app.models.notification import Notification

patient_bp = Blueprint("patient", __name__)


@patient_bp.route("/dashboard")
@role_required("patient")
def dashboard():
    """Patient personal health portal dashboard."""
    user = get_current_user()

    # Upcoming active appointments
    now = datetime.utcnow()
    upcoming_appointments = (
        Appointment.query.filter(
            Appointment.patient_id == user.id,
            Appointment.status.in_(["PENDING", "CONFIRMED"]),
            Appointment.start_datetime >= now,
        )
        .order_by(Appointment.start_datetime.asc())
        .all()
    )

    # Unread notifications
    notifications = (
        Notification.query.filter_by(user_id=user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    # Unpaid invoices
    unpaid_invoices = (
        Invoice.query.join(Appointment)
        .filter(Appointment.patient_id == user.id, Invoice.status == "UNPAID")
        .all()
    )

    return render_template(
        "patient/dashboard.html",
        user=user,
        upcoming_appointments=upcoming_appointments,
        notifications=notifications,
        unpaid_invoices=unpaid_invoices,
    )


@patient_bp.route("/profile", methods=["GET", "POST"])
@role_required("patient")
def profile():
    """View and update patient clinical demographic profile."""
    user = get_current_user()
    prof = user.patient_profile
    if not prof:
        prof = PatientProfile(user_id=user.id)
        db.session.add(prof)
        db.session.commit()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "Other")
        address = request.form.get("address", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        is_student = bool(request.form.get("is_student"))
        medical_history = request.form.get("medical_history", "").strip()

        if phone and not re.match(r"^01[3-9]\d{8}$", phone):
            flash(
                "Invalid phone. Must be a valid BD number (01XXXXXXXXX).",
                "danger",
            )
            return (
                render_template(
                    "patient/profile.html", user=user, profile=prof
                ),
                400,
            )

        if name:
            user.name = name

        if age and age.isdigit():
            prof.age = int(age)

        prof.phone = phone
        prof.gender = gender
        prof.address = address
        prof.blood_group = blood_group
        prof.is_student = is_student
        prof.medical_history = medical_history

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("patient.profile"))

    return render_template("patient/profile.html", user=user, profile=prof)


@patient_bp.route("/medical-history")
@role_required("patient")
def medical_history():
    """Patient medical and past consultation records."""
    user = get_current_user()
    past_appointments = (
        Appointment.query.filter(
            Appointment.patient_id == user.id,
            Appointment.status == "COMPLETED",
        )
        .order_by(Appointment.start_datetime.desc())
        .all()
    )
    return render_template(
        "patient/medical_history.html",
        user=user,
        profile=user.patient_profile,
        past_appointments=past_appointments,
    )
