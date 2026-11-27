from app.models.user import User
from app.models.patient import PatientProfile
from app.extensions import db


def test_patient_dashboard_requires_login(client):
    res = client.get("/dashboard")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_patient_dashboard_content(client, app):
    with app.app_context():
        u = User(name="Rahim Uddin", email="rahim@patient.test", role="patient")
        u.set_password("Pass1234!")
        db.session.add(u)
        db.session.flush()

        profile = PatientProfile(
            user_id=u.id, age=65, phone="01711223344", blood_group="A+"
        )
        db.session.add(profile)
        db.session.commit()
        uid = u.id

    # Log in as patient
    with client.session_transaction() as sess:
        sess["user_id"] = uid
        sess["user_role"] = "patient"
        sess["user_name"] = "Rahim Uddin"

    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"Rahim Uddin" in res.data
    assert b"Upcoming Appointments" in res.data


def test_patient_profile_update(client, app):
    with app.app_context():
        u = User(name="Anika", email="anika@patient.test", role="patient")
        u.set_password("Pass1234!")
        db.session.add(u)
        db.session.flush()

        profile = PatientProfile(
            user_id=u.id, age=21, phone="01722334455", is_student=False
        )
        db.session.add(profile)
        db.session.commit()
        uid = u.id

    with client.session_transaction() as sess:
        sess["user_id"] = uid
        sess["user_role"] = "patient"
        sess["user_name"] = "Anika"

    # Update profile
    res = client.post(
        "/profile",
        data={
            "name": "Anika Tabassum",
            "phone": "01722334455",
            "age": "22",
            "gender": "Female",
            "address": "Talaimari, Rajshahi",
            "blood_group": "B+",
            "is_student": "1",
            "medical_history": "Mild dust allergy",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        prof = db.session.get(PatientProfile, uid)
        assert prof.age == 22
        assert prof.blood_group == "B+"
        assert prof.is_student is True
        assert prof.medical_history == "Mild dust allergy"
        user = db.session.get(User, uid)
        assert user.name == "Anika Tabassum"
