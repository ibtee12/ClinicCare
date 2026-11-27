"""Unit test for Notification endpoints."""

from app.extensions import db
from app.models.user import User
from app.models.notification import Notification


def test_notification_flow(client, app):
    with app.app_context():
        u = User(name="Notif Patient", email="notif@test.com", role="patient")
        u.set_password("Pass123!")
        db.session.add(u)
        db.session.flush()

        n = Notification(
            user_id=u.id,
            channel="in_app",
            message="Your appointment is confirmed.",
            is_read=False,
        )
        db.session.add(n)
        db.session.commit()
        notif_id = n.id

    client.post(
        "/login",
        data={"email": "notif@test.com", "password": "Pass123!"},
        follow_redirects=True,
    )

    res = client.get("/notifications")
    assert res.status_code == 200
    assert b"Your appointment is confirmed." in res.data

    res_read = client.post(
        f"/notifications/{notif_id}/read", follow_redirects=True
    )
    assert res_read.status_code == 200

    with app.app_context():
        n_updated = db.session.get(Notification, notif_id)
        assert n_updated.is_read is True
