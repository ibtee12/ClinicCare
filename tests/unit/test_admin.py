from app.models.user import User
from app.models.doctor import Department, DoctorProfile
from app.extensions import db


def test_admin_dashboard_metrics(client, app):
    with app.app_context():
        admin_u = User(name="Admin", email="admin@test.com", role="admin")
        admin_u.set_password("AdminPass123!")
        doc_u = User(name="Doc A", email="doca@test.com", role="doctor")
        doc_u.set_password("DocPass123!")
        pat_u = User(name="Pat A", email="pata@test.com", role="patient")
        pat_u.set_password("PatPass123!")
        db.session.add_all([admin_u, doc_u, pat_u])
        db.session.flush()

        doc_prof = DoctorProfile(user_id=doc_u.id, qualifications="MBBS")
        db.session.add(doc_prof)
        db.session.commit()
        admin_id = admin_u.id

    with client.session_transaction() as sess:
        sess["user_id"] = admin_id
        sess["user_role"] = "admin"
        sess["user_name"] = "Admin"

    res = client.get("/admin/dashboard")
    assert res.status_code == 200
    assert b"Total Patients" in res.data
    assert b"Active Doctors" in res.data


def test_admin_manage_doctors(client, app):
    with app.app_context():
        admin_u = User(name="Admin", email="admin2@test.com", role="admin")
        admin_u.set_password("AdminPass123!")
        dept = Department(name="Neurology")
        db.session.add_all([admin_u, dept])
        db.session.commit()
        admin_id = admin_u.id
        dept_id = dept.id

    with client.session_transaction() as sess:
        sess["user_id"] = admin_id
        sess["user_role"] = "admin"
        sess["user_name"] = "Admin"

    # Create new doctor
    res = client.post(
        "/admin/doctors/create",
        data={
            "name": "Dr. Tanvir",
            "email": "tanvir@cliniccare.test",
            "password": "Password123!",
            "department_id": str(dept_id),
            "qualifications": "MBBS, MD",
            "fee": "900.0",
            "bio": "Neurologist",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    with app.app_context():
        u = User.query.filter_by(email="tanvir@cliniccare.test").first()
        assert u is not None
        assert u.role == "doctor"
        assert u.doctor_profile.fee == 900.0


def test_admin_reports_view(client, app):
    with app.app_context():
        admin_u = User(name="Admin", email="admin3@test.com", role="admin")
        admin_u.set_password("AdminPass123!")
        db.session.add(admin_u)
        db.session.commit()
        admin_id = admin_u.id

    with client.session_transaction() as sess:
        sess["user_id"] = admin_id
        sess["user_role"] = "admin"
        sess["user_name"] = "Admin"

    res = client.get("/admin/reports")
    assert res.status_code == 200
    assert b"Revenue" in res.data
