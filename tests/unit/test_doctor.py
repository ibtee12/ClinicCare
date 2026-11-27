from datetime import datetime, timedelta
from app.models.user import User
from app.models.doctor import Department, DoctorProfile, Availability
from app.models.appointment import Appointment
from app.extensions import db


def test_public_doctor_search_and_filter(client, app):
    with app.app_context():
        dept_cardio = Department(name="Cardiology", description="Heart Care")
        dept_derm = Department(name="Dermatology", description="Skin Care")
        db.session.add_all([dept_cardio, dept_derm])
        db.session.flush()

        doc1_user = User(
            name="Dr. Farhan", email="farhan@doc.test", role="doctor"
        )
        doc1_user.set_password("DocPass123!")
        db.session.add(doc1_user)
        db.session.flush()

        doc1_prof = DoctorProfile(
            user_id=doc1_user.id,
            department_id=dept_cardio.id,
            qualifications="MBBS, FCPS",
            fee=800.0,
            bio="Senior Cardiologist",
        )
        db.session.add(doc1_prof)
        db.session.commit()

    # Search by department filter
    res = client.get("/doctors?department=Cardiology")
    assert res.status_code == 200
    assert b"Dr. Farhan" in res.data
    assert b"Cardiology" in res.data

    # Search by doctor name query
    res_search = client.get("/doctors?q=Farhan")
    assert res_search.status_code == 200
    assert b"Dr. Farhan" in res_search.data


def test_doctor_profile_public_view_and_slots(client, app):
    with app.app_context():
        dept = Department(name="Pediatrics", description="Child Health")
        db.session.add(dept)
        db.session.flush()

        u = User(name="Dr. Sarah", email="sarah@doc.test", role="doctor")
        u.set_password("DocPass123!")
        db.session.add(u)
        db.session.flush()

        doc = DoctorProfile(
            user_id=u.id,
            department_id=dept.id,
            qualifications="MBBS, DCH",
            fee=700.0,
        )
        db.session.add(doc)
        db.session.flush()

        # Add availability on Monday (0)
        avail = Availability(
            doctor_id=u.id,
            weekday=0,
            start_time="10:00",
            end_time="11:00",
            slot_minutes=30,
        )
        db.session.add(avail)
        db.session.commit()
        doc_id = u.id

    res = client.get(f"/doctors/{doc_id}")
    assert res.status_code == 200
    assert b"Dr. Sarah" in res.data
    assert b"Pediatrics" in res.data


def test_doctor_schedule_availability_setup(client, app):
    with app.app_context():
        u = User(name="Dr. Kamal", email="kamal@doc.test", role="doctor")
        u.set_password("DocPass123!")
        db.session.add(u)
        db.session.flush()

        doc = DoctorProfile(
            user_id=u.id, qualifications="MBBS", fee=500.0
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = u.id

    with client.session_transaction() as sess:
        sess["user_id"] = doc_id
        sess["user_role"] = "doctor"
        sess["user_name"] = "Dr. Kamal"

    # POST new availability rule
    res = client.post(
        "/doctor/schedule",
        data={
            "weekday": "2",  # Wednesday
            "start_time": "14:00",
            "end_time": "16:00",
            "slot_minutes": "20",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        avails = Availability.query.filter_by(doctor_id=doc_id).all()
        assert len(avails) == 1
        assert avails[0].weekday == 2
        assert avails[0].slot_minutes == 20


def test_doctor_update_appointment_status_and_notes(client, app):
    with app.app_context():
        doc_user = User(name="Dr. Nila", email="nila@doc.test", role="doctor")
        doc_user.set_password("Pass123!")
        pat_user = User(name="Karim", email="karim2@pat.test", role="patient")
        pat_user.set_password("Pass123!")
        db.session.add_all([doc_user, pat_user])
        db.session.flush()

        doc_prof = DoctorProfile(user_id=doc_user.id, qualifications="MBBS")
        db.session.add(doc_prof)
        db.session.flush()

        apt = Appointment(
            patient_id=pat_user.id,
            doctor_id=doc_user.id,
            start_datetime=datetime.utcnow() + timedelta(days=1),
            status="PENDING",
            reason="Fever",
        )
        db.session.add(apt)
        db.session.commit()
        doc_id = doc_user.id
        apt_id = apt.id

    with client.session_transaction() as sess:
        sess["user_id"] = doc_id
        sess["user_role"] = "doctor"
        sess["user_name"] = "Dr. Nila"

    # Update appointment status to COMPLETED with notes
    res = client.post(
        f"/doctor/appointments/{apt_id}",
        data={
            "status": "COMPLETED",
            "notes": "Paracetamol 500mg TDS for 3 days. Rest well.",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        updated_apt = db.session.get(Appointment, apt_id)
        assert updated_apt.status == "COMPLETED"
        assert "Paracetamol" in updated_apt.notes
