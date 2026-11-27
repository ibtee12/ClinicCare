"""Doctor portal: daily schedule, availability management, visit notes."""

from datetime import datetime, time
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from app.extensions import db
from app.routes.auth import role_required, get_current_user
from app.models.doctor import Availability
from app.models.appointment import Appointment
from app.patterns.observer import get_appointment_subject, AppointmentEvent

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


@doctor_bp.route("/dashboard")
@role_required("doctor")
def dashboard():
    """Doctor daily consultations dashboard."""
    user = get_current_user()
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    today_end = datetime.combine(datetime.utcnow().date(), time.max)

    # Today's appointments
    today_appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == user.id,
            Appointment.start_datetime >= today_start,
            Appointment.start_datetime <= today_end,
        )
        .order_by(Appointment.start_datetime.asc())
        .all()
    )

    # Upcoming all appointments
    upcoming_appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == user.id,
            Appointment.start_datetime > today_end,
            Appointment.status.in_(["PENDING", "CONFIRMED"]),
        )
        .order_by(Appointment.start_datetime.asc())
        .limit(10)
        .all()
    )

    return render_template(
        "doctor/dashboard.html",
        user=user,
        today_appointments=today_appointments,
        upcoming_appointments=upcoming_appointments,
    )


@doctor_bp.route("/schedule", methods=["GET", "POST"])
@role_required("doctor")
def schedule():
    """Configure recurring weekly availability slot rules."""
    user = get_current_user()

    if request.method == "POST":
        weekday = int(request.form.get("weekday", 0))
        start_time = request.form.get("start_time", "09:00").strip()
        end_time = request.form.get("end_time", "13:00").strip()
        slot_minutes = int(request.form.get("slot_minutes", 20))

        if start_time >= end_time:
            flash("Start time must precede end time.", "danger")
            return redirect(url_for("doctor.schedule"))

        avail = Availability(
            doctor_id=user.id,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            slot_minutes=slot_minutes,
        )
        db.session.add(avail)
        db.session.commit()
        flash("Availability schedule rule added successfully!", "success")
        return redirect(url_for("doctor.schedule"))

    availabilities = (
        Availability.query.filter_by(doctor_id=user.id)
        .order_by(Availability.weekday.asc(), Availability.start_time.asc())
        .all()
    )
    weekday_names = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]
    return render_template(
        "doctor/schedule.html",
        user=user,
        availabilities=availabilities,
        weekday_names=weekday_names,
    )


@doctor_bp.route("/schedule/delete/<int:avail_id>", methods=["POST"])
@role_required("doctor")
def delete_availability(avail_id: int):
    """Remove availability rule."""
    user = get_current_user()
    avail = Availability.query.filter_by(
        id=avail_id, doctor_id=user.id
    ).first_or_404()
    db.session.delete(avail)
    db.session.commit()
    flash("Availability rule removed.", "info")
    return redirect(url_for("doctor.schedule"))


@doctor_bp.route("/appointments/<int:apt_id>", methods=["GET", "POST"])
@role_required("doctor")
def appointment_detail(apt_id: int):
    """View appointment details, update status, and record clinical notes."""
    user = get_current_user()
    apt = Appointment.query.filter_by(
        id=apt_id, doctor_id=user.id
    ).first()
    if not apt:
        abort(404)

    if request.method == "POST":
        new_status = request.form.get("status", apt.status).strip()
        notes = request.form.get("notes", "").strip()

        old_status = apt.status
        apt.status = new_status
        if notes:
            apt.notes = notes
        db.session.commit()

        # Fire observer event if status changed
        if old_status != new_status:
            subject = get_appointment_subject()
            event = AppointmentEvent(
                event_type=new_status,
                appointment_id=apt.id,
                patient_id=apt.patient_id,
                doctor_id=apt.doctor_id,
                payload={"notes": notes, "old_status": old_status},
            )
            subject.notify(event)

        flash(f"Appointment status updated to {new_status}.", "success")
        return redirect(url_for("doctor.dashboard"))

    return render_template("doctor/appointment_detail.html", apt=apt)
