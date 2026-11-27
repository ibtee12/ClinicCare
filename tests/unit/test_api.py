from datetime import date
from app.models.user import User
from app.models.doctor import Department, DoctorProfile, Availability
from app.extensions import db


def test_api_v1_doctors_list(client, app):
    with app.app_context():
        dept = Department(name="Dentistry")
        db.session.add(dept)
        db.session.flush()

        u = User(name="Dr. Dental", email="dent@doc.test", role="doctor")
        u.set_password("Pass123!")
        db.session.add(u)
        db.session.flush()

        doc = DoctorProfile(
            user_id=u.id,
            department_id=dept.id,
            qualifications="BDS",
            fee=600.0,
        )
        db.session.add(doc)
        db.session.commit()

    res = client.get("/api/v1/doctors")
    assert res.status_code == 200
    json_data = res.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert json_data[0]["name"] == "Dr. Dental"
    assert json_data[0]["department"] == "Dentistry"


def test_api_v1_available_slots(client, app):
    with app.app_context():
        u = User(name="Dr. Slot", email="slot@doc.test", role="doctor")
        u.set_password("Pass123!")
        db.session.add(u)
        db.session.flush()

        doc = DoctorProfile(user_id=u.id, qualifications="MBBS")
        db.session.add(doc)
        db.session.flush()

        today_weekday = date.today().weekday()
        avail = Availability(
            doctor_id=u.id,
            weekday=today_weekday,
            start_time="09:00",
            end_time="10:00",
            slot_minutes=30,
        )
        db.session.add(avail)
        db.session.commit()
        doc_id = u.id

    iso_today = date.today().isoformat()
    res = client.get(f"/api/v1/doctors/{doc_id}/slots?date={iso_today}")
    assert res.status_code == 200
    slots = res.get_json()
    assert len(slots) == 2
    assert slots[0]["time"] == "09:00"
