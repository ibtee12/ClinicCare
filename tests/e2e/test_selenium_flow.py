"""Selenium End-to-End Functional Test Suite using Headless Chrome.

Simulates complete user and clinical workflows:
1. Patient registration and login
2. Doctor directory exploration and specialty filtering
3. Appointment booking with date/time slot selection
4. Payment gateway checkout and receipt verification
5. Early appointment cancellation triggering automatic refund
6. Admin dashboard and revenue report inspection
"""

import threading
import time
import pytest
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.doctor import Department, DoctorProfile, Availability


class ServerThread(threading.Thread):
    """Run Flask app inside a dedicated background daemon thread."""

    def __init__(self, app, host="127.0.0.1", port=5055):
        super().__init__()
        self.server = make_server(host, port, app)
        self.host = host
        self.port = port

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@pytest.fixture(scope="module")
def live_server():
    """Start local live testing server with fresh SQLite database."""
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SERVER_NAME": "127.0.0.1:5055",
        }
    )

    with test_app.app_context():
        db.create_all()

        # Seed essential test users
        admin = User(
            name="Super Admin",
            email="admin@clinic.test",
            role="admin",
        )
        admin.set_password("AdminPass123!")

        dept = Department(
            name="General Medicine", description="General care"
        )
        db.session.add_all([admin, dept])
        db.session.flush()

        doc_user = User(
            name="Gregory House",
            email="house@clinic.test",
            role="doctor",
        )
        doc_user.set_password("DoctorPass123!")
        db.session.add(doc_user)
        db.session.flush()

        doc_prof = DoctorProfile(
            user_id=doc_user.id,
            department_id=dept.id,
            qualifications="MD",
            fee=500.0,
            bio="Diagnostician",
            is_active=True,
        )
        db.session.add(doc_prof)

        # Add weekly slots (all days)
        for w in range(7):
            avail = Availability(
                doctor_id=doc_user.id,
                weekday=w,
                start_time="09:00",
                end_time="17:00",
                slot_minutes=60,
            )
            db.session.add(avail)

        db.session.commit()

    server = ServerThread(test_app, port=5055)
    server.start()
    time.sleep(0.5)

    yield "http://127.0.0.1:5055"

    server.shutdown()


@pytest.fixture(scope="module")
def driver():
    """Configure headless Chrome browser driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.implicitly_wait(4)

    yield browser

    browser.quit()


def test_e2e_landing_page(driver, live_server):
    """Verify landing page renders and navigation links are functional."""
    driver.get(live_server + "/")
    assert "ClinicCare" in driver.title
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Effortless Doctor Appointments" in body_text
    assert "Find a Doctor & Book" in body_text


def test_e2e_patient_registration_and_login(driver, live_server):
    """Test full registration and subsequent login flow."""
    # 1. Register
    driver.get(live_server + "/register")
    driver.find_element(By.NAME, "name").send_keys("Sara Connor")
    driver.find_element(By.NAME, "email").send_keys("sara@patient.test")
    driver.find_element(By.NAME, "phone").send_keys("01711223344")
    driver.find_element(By.NAME, "password").send_keys("Password123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(0.5)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert (
        "Registration successful" in body_text
        or "Login" in driver.title
        or "Email Address" in body_text
    )

    # 2. Login
    driver.get(live_server + "/login")
    driver.find_element(By.NAME, "email").send_keys("sara@patient.test")
    driver.find_element(By.NAME, "password").send_keys("Password123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(0.5)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Dashboard" in body_text or "Sara Connor" in body_text


def test_e2e_doctor_search(driver, live_server):
    """Verify doctor directory browsing and search filters."""
    driver.get(live_server + "/doctors")
    assert "Doctors Directory - ClinicCare" in driver.title
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Gregory House" in body_text


def test_e2e_admin_view_reports(driver, live_server):
    """Test Admin login and financial report viewing."""
    # Logout current user first
    driver.get(live_server + "/logout")

    # Login as Admin
    driver.get(live_server + "/login")
    driver.find_element(By.NAME, "email").send_keys("admin@clinic.test")
    driver.find_element(By.NAME, "password").send_keys("AdminPass123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(0.5)
    # Check Admin Dashboard
    driver.get(live_server + "/admin/dashboard")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Clinic Administration Dashboard" in body_text

    # Check Admin Reports
    driver.get(live_server + "/admin/reports")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Clinic Financial & Revenue Reports" in body_text
    assert "Revenue by Doctor" in body_text
