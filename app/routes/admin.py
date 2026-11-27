"""Admin clinic management, doctor rostering and financial reports."""

from datetime import datetime, time
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from app.extensions import db
from app.routes.auth import role_required
from app.models.user import User
from app.models.doctor import Department, DoctorProfile
from app.models.appointment import Appointment
from app.models.billing import Invoice

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    """Clinic administration summary metrics."""
    total_patients = User.query.filter_by(role="patient").count()
    active_doctors = DoctorProfile.query.filter_by(is_active=True).count()

    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    today_end = datetime.combine(datetime.utcnow().date(), time.max)
    appointments_today = Appointment.query.filter(
        Appointment.start_datetime >= today_start,
        Appointment.start_datetime <= today_end,
    ).count()

    paid_invoices = Invoice.query.filter_by(status="PAID").all()
    total_revenue = sum(inv.total for inv in paid_invoices)

    recent_appointments = (
        Appointment.query.order_by(Appointment.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_patients=total_patients,
        active_doctors=active_doctors,
        appointments_today=appointments_today,
        total_revenue=total_revenue,
        recent_appointments=recent_appointments,
    )


@admin_bp.route("/doctors")
@role_required("admin")
def list_doctors():
    """Manage doctor roster and departments."""
    doctors = DoctorProfile.query.all()
    return render_template("admin/doctors.html", doctors=doctors)


@admin_bp.route("/doctors/create", methods=["GET", "POST"])
@role_required("admin")
def create_doctor():
    """Register a new clinical specialist."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        dept_id = request.form.get("department_id")
        qualifications = request.form.get("qualifications", "").strip()
        fee = float(request.form.get("fee", 500.0) or 500.0)
        bio = request.form.get("bio", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("admin.create_doctor"))

        user = User(name=name, email=email, role="doctor")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        profile = DoctorProfile(
            user_id=user.id,
            department_id=int(dept_id) if dept_id else None,
            qualifications=qualifications,
            fee=fee,
            bio=bio,
            is_active=True,
        )
        db.session.add(profile)
        db.session.commit()

        flash(f"Doctor Dr. {name} registered successfully!", "success")
        return redirect(url_for("admin.list_doctors"))

    departments = Department.query.all()
    return render_template(
        "admin/doctor_create.html", departments=departments
    )


@admin_bp.route("/doctors/toggle/<int:user_id>", methods=["POST"])
@role_required("admin")
def toggle_doctor(user_id: int):
    """Activate or deactivate a doctor."""
    doc = DoctorProfile.query.filter_by(user_id=user_id).first_or_404()
    doc.is_active = not doc.is_active
    db.session.commit()
    status_str = "activated" if doc.is_active else "deactivated"
    flash(f"Doctor account {status_str}.", "info")
    return redirect(url_for("admin.list_doctors"))


@admin_bp.route("/departments", methods=["GET", "POST"])
@role_required("admin")
def departments():
    """Manage medical departments."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name:
            dept = Department(name=name, description=description)
            db.session.add(dept)
            db.session.commit()
            flash(f"Department '{name}' created.", "success")
            return redirect(url_for("admin.departments"))

    depts = Department.query.all()
    return render_template("admin/departments.html", departments=depts)


@admin_bp.route("/appointments")
@role_required("admin")
def appointments():
    """All clinic appointments filtered by status, doctor, or date."""
    status = request.args.get("status")
    doctor_id = request.args.get("doctor_id")

    query = Appointment.query

    if status:
        query = query.filter(Appointment.status == status)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == int(doctor_id))

    all_appointments = (
        query.order_by(Appointment.start_datetime.desc()).limit(50).all()
    )
    doctors = DoctorProfile.query.all()

    return render_template(
        "admin/appointments.html",
        appointments=all_appointments,
        doctors=doctors,
        selected_status=status,
        selected_doctor=int(doctor_id) if doctor_id else None,
    )


@admin_bp.route("/reports")
@role_required("admin")
def reports():
    """Clinic financial revenue breakdown by doctor and by month."""
    paid_invoices = Invoice.query.filter_by(status="PAID").all()

    # Revenue by doctor
    doctor_revenue = {}
    for inv in paid_invoices:
        doc_name = inv.appointment.doctor.user.name
        doctor_revenue[doc_name] = (
            doctor_revenue.get(doc_name, 0.0) + inv.total
        )

    # Monthly revenue aggregation
    monthly_revenue = {}
    for inv in paid_invoices:
        month_key = inv.created_at.strftime("%b %Y")
        monthly_revenue[month_key] = (
            monthly_revenue.get(month_key, 0.0) + inv.total
        )

    total_revenue = sum(inv.total for inv in paid_invoices)

    return render_template(
        "admin/reports.html",
        doctor_revenue=doctor_revenue,
        monthly_revenue=monthly_revenue,
        total_revenue=total_revenue,
    )
