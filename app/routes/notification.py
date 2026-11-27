"""Notification list and mark-as-read endpoints."""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from app.extensions import db
from app.routes.auth import login_required
from app.models.notification import Notification

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/notifications")
@login_required
def list_notifications():
    """Display logged in user's in-app notifications."""
    user_id = session.get("user_id")
    notifications = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template(
        "notification/list.html", notifications=notifications
    )


@notification_bp.route(
    "/notifications/<int:notification_id>/read", methods=["POST"]
)
@login_required
def mark_read(notification_id: int):
    """Mark a notification as read."""
    user_id = session.get("user_id")
    notif = Notification.query.filter_by(
        id=notification_id, user_id=user_id
    ).first_or_404()
    notif.is_read = True
    db.session.commit()
    flash("Notification marked as read.", "success")
    return redirect(url_for("notification.list_notifications"))
