from app.models.user import User
from app.extensions import db


def test_password_hashing():
    u = User(name="Rahim", email="rahim@test.com", role="patient")
    u.set_password("SecretPass123!")
    assert u.password_hash != "SecretPass123!"
    assert u.check_password("SecretPass123!") is True
    assert u.check_password("WrongPass") is False


def test_registration_success(client):
    res = client.post(
        "/register",
        data={
            "name": "Karim Hossain",
            "email": "karim@test.com",
            "password": "Password123!",
            "phone": "01711223344",
            "role": "patient",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    user = User.query.filter_by(email="karim@test.com").first()
    assert user is not None
    assert user.name == "Karim Hossain"
    assert user.role == "patient"


def test_registration_duplicate_email(client):
    client.post(
        "/register",
        data={
            "name": "User 1",
            "email": "dup@test.com",
            "password": "Password123!",
            "phone": "01711223344",
        },
    )
    res = client.post(
        "/register",
        data={
            "name": "User 2",
            "email": "dup@test.com",
            "password": "Password123!",
            "phone": "01711223355",
        },
    )
    assert res.status_code == 400
    assert b"Email already registered" in res.data


def test_login_and_logout(client, app):
    with app.app_context():
        u = User(name="Test Patient", email="login@test.com", role="patient")
        u.set_password("CorrectPass123!")
        db.session.add(u)
        db.session.commit()

    # Success login
    res = client.post(
        "/login",
        data={"email": "login@test.com", "password": "CorrectPass123!"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Logged in successfully" in res.data or b"Dashboard" in res.data

    # Logout
    logout_res = client.get("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"Logged out" in logout_res.data or b"Login" in logout_res.data


def test_login_invalid_password(client, app):
    with app.app_context():
        u = User(name="Test Patient", email="login2@test.com", role="patient")
        u.set_password("CorrectPass123!")
        db.session.add(u)
        db.session.commit()

    res = client.post(
        "/login",
        data={"email": "login2@test.com", "password": "WrongPassword"},
        follow_redirects=True,
    )
    assert res.status_code == 401
    assert b"Invalid email or password" in res.data


def test_role_required_forbidden_403(client, app):
    # Patient trying to access doctor route
    with app.app_context():
        u = User(name="Regular Patient", email="p@test.com", role="patient")
        u.set_password("Pass1234!")
        db.session.add(u)
        db.session.commit()

    client.post(
        "/login",
        data={"email": "p@test.com", "password": "Pass1234!"},
        follow_redirects=True,
    )

    # Doctor route should return 403
    res = client.get("/doctor/schedule")
    assert res.status_code == 403
    assert b"Access Denied" in res.data or b"403" in res.data
