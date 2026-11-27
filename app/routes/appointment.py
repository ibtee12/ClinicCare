"""Appointment scheduling and lifecycle routes."""

from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
)
from app.extensions import db
from app.routes.auth import role_required, get_current_user
from app.models.doctor import DoctorProfile
from app.models.appointment import Appointment
from app.models.billing import Invoice
from app.patterns.strategy import select_best_discount
from app.patterns.observer import get_appointment_subject, AppointmentEvent

appointment_bp = Blueprint("appointment", __name__)


@appointment_bp.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@role_required("patient")
def book(doctor_id: int):
    """Book consultation slot and generate billing invoice."""
    user = get_current_user()
    doctor = DoctorProfile.query.filter_by(
        user_id=doctor_id, is_active=True
    ).first_or_404()

    if request.method == "POST":
        slot_time_str = request.form.get("slot_time", "").strip()
        reason = request.form.get("reason", "").strip()
        promo_code = request.form.get("promo_code", "").strip()

        try:
            slot_dt = datetime.strptime(slot_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Invalid appointment time format.", "danger")
            return redirect(
                url_for("public.doctor_detail", doctor_id=doctor_id)
            )

        now = datetime.utcnow()
        if slot_dt < now:
            flash("Cannot book appointment in the past.", "danger")
            return (
                render_template(
                    "appointment/book.html",
                    doctor=doctor,
                    slot_time=slot_time_str,
                ),
                400,
            )

        if (slot_dt - now).days > 60:
            flash(
                "Cannot book appointment beyond 60 days in advance.", "danger"
            )
            return (
                render_template(
                    "appointment/book.html",
                    doctor=doctor,
                    slot_time=slot_time_str,
                ),
                400,
            )

        # Double booking check
        existing = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_datetime == slot_dt,
            Appointment.status.notin_(["CANCELLED"]),
        ).first()

        if existing:
            flash(
                "Slot is already booked. Please choose another slot.",
                "danger",
            )
            return (
                render_template(
                    "appointment/book.html",
                    doctor=doctor,
                    slot_time=slot_time_str,
                ),
                400,
            )

        # Calculate best eligible discount using Strategy pattern
        prof = user.patient_profile
        prior_visits = Appointment.query.filter_by(
            patient_id=user.id, status="COMPLETED"
        ).count()

        patient_info = {
            "age": prof.age if prof else 30,
            "is_student": prof.is_student if prof else False,
            "prior_visits_count": prior_visits,
            "promo_code": promo_code,
        }

        best_name, discount_amount, final_total = select_best_discount(
            doctor.fee, patient_info
        )

        # Create appointment and invoice
        apt = Appointment(
            patient_id=user.id,
            doctor_id=doctor_id,
            start_datetime=slot_dt,
            status="PENDING",
            reason=reason,
        )
        db.session.add(apt)
        db.session.flush()

        invoice = Invoice(
            appointment_id=apt.id,
            base_fee=doctor.fee,
            discount_amount=discount_amount,
            discount_name=best_name,
            total=final_total,
            status="UNPAID",
        )
        db.session.add(invoice)
        db.session.commit()

        # Fire observer event
        subject = get_appointment_subject()
        event = AppointmentEvent(
            event_type="CREATED",
            appointment_id=apt.id,
            patient_id=user.id,
            doctor_id=doctor_id,
            payload={"fee": final_total, "discount": best_name},
        )
        subject.notify(event)

        flash(
            f"Appointment reserved! Invoice generated with {best_name}.",
            "success",
        )
        if "billing.pay_invoice" in current_app.view_functions:
            return redirect(
                url_for("billing.pay_invoice", invoice_id=invoice.id)
            )
        return redirect(url_for("appointment.list_appointments"))

    slot_time_str = request.args.get("time", "")
    return render_template(
        "appointment/book.html", doctor=doctor, slot_time=slot_time_str
    )


@appointment_bp.route("/appointments")
@role_required("patient")
def list_appointments():
    """List all scheduled and historical appointments for current patient."""
    user = get_current_user()
    appointments = (
        Appointment.query.filter_by(patient_id=user.id)
        .order_by(Appointment.start_datetime.desc())
        .all()
    )
    now = datetime.utcnow()
    return render_template(
        "appointment/list.html",
        appointments=appointments,
        now=now,
    )


@appointment_bp.route("/appointments/cancel/<int:apt_id>", methods=["POST"])
@role_required("patient")
def cancel_appointment(apt_id: int):
    """Cancel appointment with automated refund evaluation."""
    user = get_current_user()
    apt = Appointment.query.filter_by(
        id=apt_id, patient_id=user.id
    ).first()
    if not apt:
        abort(404)

    if apt.status == "CANCELLED":
        flash("Appointment is already cancelled.", "info")
        return redirect(url_for("appointment.list_appointments"))

    now = datetime.utcnow()
    hours_before = (apt.start_datetime - now).total_seconds() / 3600.0

    if hours_before < 2.0:
        flash(
            "Cancellation not permitted within 2 hours of appointment start.",
            "danger",
        )
        appointments = (
            Appointment.query.filter_by(patient_id=user.id)
            .order_by(Appointment.start_datetime.desc())
            .all()
        )
        return (
            render_template(
                "appointment/list.html",
                appointments=appointments,
                now=now,
            ),
            400,
        )

    apt.status = "CANCELLED"

    # Evaluate refund if invoice was paid
    is_paid = apt.invoice and apt.invoice.status == "PAID"
    fee = apt.invoice.total if apt.invoice else 0.0

    if is_paid:
        apt.invoice.status = "REFUNDED"

    db.session.commit()

    # Notify observers
    subject = get_appointment_subject()
    event = AppointmentEvent(
        event_type="CANCELLED",
        appointment_id=apt.id,
        patient_id=user.id,
        doctor_id=apt.doctor_id,
        payload={"hours_before": hours_before, "fee": fee, "paid": is_paid},
    )
    subject.notify(event)

    if is_paid:
        refund_pct = "100%" if hours_before >= 24.0 else "50%"
        msg = (
            f"Appointment cancelled. Automated refund ({refund_pct}) "
            f"processed."
        )
        flash(msg, "success")
    else:
        flash("Appointment cancelled successfully.", "info")

    return redirect(url_for("appointment.list_appointments"))


@appointment_bp.route(
    "/appointments/reschedule/<int:apt_id>", methods=["GET", "POST"]
)
@role_required("patient")
def reschedule(apt_id: int):
    """Reschedule appointment to a new open slot."""
    user = get_current_user()
    apt = Appointment.query.filter_by(
        id=apt_id, patient_id=user.id
    ).first_or_404()

    now = datetime.utcnow()
    hours_before = (apt.start_datetime - now).total_seconds() / 3600.0
    if hours_before < 2.0:
        flash(
            "Rescheduling is not permitted within 2 hours of scheduled slot.",
            "danger",
        )
        return redirect(url_for("appointment.list_appointments")), 400

    if request.method == "POST":
        new_time_str = request.form.get("new_slot_time", "").strip()
        try:
            new_dt = datetime.strptime(new_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for("appointment.reschedule", apt_id=apt.id))

        if new_dt < datetime.utcnow():
            flash("Cannot reschedule to a past time.", "danger")
            return redirect(url_for("appointment.reschedule", apt_id=apt.id))

        # Check double booking
        conflict = Appointment.query.filter(
            Appointment.doctor_id == apt.doctor_id,
            Appointment.start_datetime == new_dt,
            Appointment.id != apt.id,
            Appointment.status.notin_(["CANCELLED"]),
        ).first()

        if conflict:
            flash("Chosen slot is no longer available.", "danger")
            return redirect(url_for("appointment.reschedule", apt_id=apt.id))

        old_dt = apt.start_datetime
        apt.start_datetime = new_dt
        db.session.commit()

        # Fire observer
        subject = get_appointment_subject()
        subject.notify(
            AppointmentEvent(
                event_type="RESCHEDULED",
                appointment_id=apt.id,
                patient_id=user.id,
                doctor_id=apt.doctor_id,
                payload={"old_time": old_dt, "new_time": new_dt},
            )
        )

        flash("Appointment rescheduled successfully!", "success")
        return redirect(url_for("appointment.list_appointments"))

    suggested = (datetime.utcnow() + timedelta(days=1)).strftime(
        "%Y-%m-%d 10:00"
    )
    return render_template(
        "appointment/reschedule.html", apt=apt, suggested_time=suggested
    )
