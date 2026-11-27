"""Authentication Blueprint and Role-Based Access Control (RBAC) Guards."""

import re
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g,
    abort,
)
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def get_current_user():
    """Retrieve logged-in user from session if authenticated."""
    if "user_id" not in session:
        return None
    if not hasattr(g, "current_user") or g.current_user is None:
        g.current_user = db.session.get(User, session["user_id"])
    return g.current_user


def login_required(f):
    """Decorator requiring an active user session."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    """Decorator enforcing Role-Based Access Control on routes."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if user is None:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            if user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Patient registration route with input validation."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        role = request.form.get("role", "patient").strip()

        # Input validation
        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template("auth/register.html"), 400

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("auth/register.html"), 400

        # Bangladeshi Phone number format validation: 01XXXXXXXXX
        if phone and not re.match(r"^01[3-9]\d{8}$", phone):
            flash(
                "Invalid phone. Must be a valid BD number (01XXXXXXXXX).",
                "danger",
            )
            return render_template("auth/register.html"), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return render_template("auth/register.html"), 400

        # Create user
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # If patient, create initial patient profile
        if role == "patient":
            from app.models.patient import PatientProfile

            profile = PatientProfile(
                user_id=user.id,
                phone=phone,
                age=int(request.form.get("age", 25) or 25),
                gender=request.form.get("gender", "Other"),
                address=request.form.get("address", ""),
                is_student=bool(request.form.get("is_student")),
            )
            db.session.add(profile)

        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    from flask import current_app

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html"), 401

        session["user_id"] = user.id
        session["user_role"] = user.role
        session["user_name"] = user.name
        flash(f"Welcome back, {user.name}!", "success")

        next_page = request.args.get("next")
        if next_page and not next_page.startswith("//"):
            return redirect(next_page)

        # Role-based landing redirects
        if user.role == "patient":
            target = (
                url_for("patient.dashboard")
                if "patient.dashboard" in current_app.view_functions
                else "/dashboard"
            )
            return redirect(target)
        elif user.role == "doctor":
            target = (
                url_for("doctor.dashboard")
                if "doctor.dashboard" in current_app.view_functions
                else "/doctor/dashboard"
            )
            return redirect(target)
        elif user.role == "admin":
            target = (
                url_for("admin.dashboard")
                if "admin.dashboard" in current_app.view_functions
                else "/admin/dashboard"
            )
            return redirect(target)
        return redirect(
            url_for("public.index")
            if "public.index" in current_app.view_functions
            else "/"
        )

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and log user out."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
