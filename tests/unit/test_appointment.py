from datetime import datetime, timedelta
from app.models.user import User
from app.models.doctor import Department, DoctorProfile
from app.models.appointment import Appointment
from app.models.billing import Invoice
from app.extensions import db


def setup_doctor_and_patient(app):
    with app.app_context():
        dept = Department(name="General Medicine")
        db.session.add(dept)
        db.session.flush()

        doc_user = User(name="Dr. Kabir", email="kabir@doc.test", role="doctor")
        doc_user.set_password("DocPass123!")
        pat_user = User(name="Hasan", email="hasan@pat.test", role="patient")
        pat_user.set_password("PatPass123!")
        db.session.add_all([doc_user, pat_user])
        db.session.flush()

        doc_prof = DoctorProfile(
            user_id=doc_user.id,
            department_id=dept.id,
            qualifications="MBBS",
            fee=500.0,
        )
        db.session.add(doc_prof)
        db.session.commit()
        return doc_user.id, pat_user.id


def test_appointment_booking_success(client, app):
    doc_id, pat_id = setup_doctor_and_patient(app)
    future_time = datetime.utcnow() + timedelta(days=2)
    time_str = future_time.strftime("%Y-%m-%d %H:%M")

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Hasan"

    res = client.post(
        f"/book/{doc_id}",
        data={
            "slot_time": time_str,
            "reason": "Routine Health Screening",
            "promo_code": "",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        apt = Appointment.query.filter_by(patient_id=pat_id, doctor_id=doc_id).first()
        assert apt is not None
        assert apt.status == "PENDING"
        assert apt.invoice is not None
        assert apt.invoice.base_fee == 500.0
        assert apt.invoice.status == "UNPAID"


def test_appointment_prevent_double_booking(client, app):
    doc_id, pat_id = setup_doctor_and_patient(app)
    future_time = datetime.utcnow() + timedelta(days=3)
    time_str = future_time.strftime("%Y-%m-%d %H:%M")

    with app.app_context():
        # Pre-existing booking at this slot
        existing = Appointment(
            patient_id=pat_id,
            doctor_id=doc_id,
            start_datetime=datetime.strptime(time_str, "%Y-%m-%d %H:%M"),
            status="CONFIRMED",
        )
        db.session.add(existing)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Hasan"

    # Second patient/attempt to book same slot
    res = client.post(
        f"/book/{doc_id}",
        data={"slot_time": time_str, "reason": "Another issue"},
        follow_redirects=True,
    )
    assert res.status_code == 400
    assert b"already booked" in res.data or b"Slot is no longer available" in res.data


def test_appointment_cannot_book_in_past(client, app):
    doc_id, pat_id = setup_doctor_and_patient(app)
    past_time = datetime.utcnow() - timedelta(days=1)
    time_str = past_time.strftime("%Y-%m-%d %H:%M")

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Hasan"

    res = client.post(
        f"/book/{doc_id}",
        data={"slot_time": time_str, "reason": "Checkup"},
        follow_redirects=True,
    )
    assert res.status_code == 400
    assert b"Cannot book appointment in the past" in res.data


def test_appointment_cannot_book_beyond_60_days(client, app):
    doc_id, pat_id = setup_doctor_and_patient(app)
    far_future = datetime.utcnow() + timedelta(days=65)
    time_str = far_future.strftime("%Y-%m-%d %H:%M")

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Hasan"

    res = client.post(
        f"/book/{doc_id}",
        data={"slot_time": time_str, "reason": "Checkup"},
        follow_redirects=True,
    )
    assert res.status_code == 400
    assert b"60 days" in res.data


def test_appointment_cancel_forbidden_under_2_hours(client, app):
    doc_id, pat_id = setup_doctor_and_patient(app)
    # Starts in 1 hour
    soon_time = datetime.utcnow() + timedelta(hours=1)

    with app.app_context():
        apt = Appointment(
            patient_id=pat_id,
            doctor_id=doc_id,
            start_datetime=soon_time,
            status="CONFIRMED",
        )
        db.session.add(apt)
        db.session.commit()
        apt_id = apt.id

    with client.session_transaction() as sess:
        sess["user_id"] = pat_id
        sess["user_role"] = "patient"
        sess["user_name"] = "Hasan"

    res = client.post(f"/appointments/cancel/{apt_id}", follow_redirects=True)
    assert res.status_code == 400
    assert b"within 2 hours" in res.data
