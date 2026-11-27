"""Billing and payment routes using Adapter pattern."""

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
from app.models.billing import Invoice, Payment
from app.models.appointment import Appointment
from app.patterns.adapter import get_payment_adapter
from app.patterns.observer import get_appointment_subject, AppointmentEvent

billing_bp = Blueprint("billing", __name__)


@billing_bp.route("/invoices")
@role_required("patient")
def list_invoices():
    """List all consultation invoices for logged-in patient."""
    user = get_current_user()
    invoices = (
        Invoice.query.join(Appointment)
        .filter(Appointment.patient_id == user.id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
    return render_template("billing/invoices.html", invoices=invoices)


@billing_bp.route("/invoices/<int:invoice_id>")
@role_required("patient", "admin", "doctor")
def invoice_detail(invoice_id: int):
    """Printable invoice receipt view."""
    user = get_current_user()
    inv = db.session.get(Invoice, invoice_id)
    if not inv:
        abort(404)

    # Patient can only view their own invoice
    if user.role == "patient" and inv.appointment.patient_id != user.id:
        abort(403)

    return render_template("billing/invoice_detail.html", invoice=inv)


@billing_bp.route("/pay/<int:invoice_id>", methods=["GET", "POST"])
@role_required("patient")
def pay_invoice(invoice_id: int):
    """Process online payment via PaymentGateway Adapter."""
    user = get_current_user()
    inv = db.session.get(Invoice, invoice_id)
    if not inv or inv.appointment.patient_id != user.id:
        abort(404)

    if inv.status == "PAID":
        flash("This invoice has already been settled.", "info")
        return redirect(url_for("billing.invoice_detail", invoice_id=inv.id))

    if request.method == "POST":
        method = request.form.get("method", "card").strip().lower()

        try:
            adapter = get_payment_adapter(method)
            result = adapter.process_payment(inv.total, request.form)
        except ValueError as e:
            flash(str(e), "danger")
            return (
                render_template("billing/pay.html", invoice=inv),
                400,
            )

        if result.success:
            payment = Payment(
                invoice_id=inv.id,
                method=method,
                amount=inv.total,
                status="PAID",
                transaction_ref=result.transaction_ref,
            )
            db.session.add(payment)
            inv.status = "PAID"
            inv.appointment.status = "CONFIRMED"
            db.session.commit()

            # Fire confirmation observers
            subject = get_appointment_subject()
            subject.notify(
                AppointmentEvent(
                    event_type="CONFIRMED",
                    appointment_id=inv.appointment_id,
                    patient_id=user.id,
                    doctor_id=inv.appointment.doctor_id,
                    payload={
                        "invoice_id": inv.id,
                        "transaction_ref": result.transaction_ref,
                    },
                )
            )

            flash(
                "Payment successful! Your appointment is confirmed.", "success"
            )
            return redirect(
                url_for("billing.invoice_detail", invoice_id=inv.id)
            )
        else:
            flash(result.message, "danger")
            if result.retryable:
                flash(
                    "Network issue encountered. You may retry payment safely.",
                    "warning",
                )
            return (
                render_template("billing/pay.html", invoice=inv),
                400,
            )

    return render_template("billing/pay.html", invoice=inv)
