"""In-app and outbox notification models."""

from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    """System notification dispatched to a user."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    channel = db.Column(
        db.String(20), nullable=False, default="in_app"
    )  # in_app, email, sms
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<Notification #{self.id} "
            f"user={self.user_id} read={self.is_read}>"
        )
