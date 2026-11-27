# ClinicCare 🏥

[![ClinicCare CI](https://github.com/ibtee12/ClinicCare/actions/workflows/ci.yml/badge.svg)](https://github.com/ibtee12/ClinicCare/actions/workflows/ci.yml)
[![Coverage Status](https://img.shields.io/badge/Coverage-85%25-brightgreen.svg)](#testing)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ClinicCare is a clinic appointment and billing web application engineered for **RUET CSE 3206 Software Engineering Sessional**. It is designed with clean software architecture principles, featuring 5 classic Gang of Four (GoF) design patterns, robust role-based access control (RBAC), simulated online payments, automated notifications, comprehensive test coverage (unit, mock, and end-to-end Selenium), and automated GitHub Actions CI/CD.

---

## 🌟 Key Features

- **Role-Based Access Control (RBAC):** Distinct dashboards and access rules for **Patients**, **Doctors**, and **Clinic Administrators**.
- **Dynamic Slot Scheduling:** Doctor availability schedules automatically generate bookable slots, preventing double-booking.
- **Strategy Pattern Billing:** Dynamic calculation of best single discount (Senior Citizen 20%, Student 15%, First-Visit 10%, Promo Code) without stacking.
- **Adapter Pattern Payments:** Simulated multi-gateway architecture supporting Card and Mobile Wallet (bKash/Nagad) checkouts.
- **Observer Pattern Notifications:** Lifecycle status changes (`CONFIRMED`, `COMPLETED`, `CANCELLED`, `REFUNDED`) automatically trigger notifications and invoice adjustments.
- **Factory Pattern Dispatcher:** Seamless decoupling of notification delivery across In-App, Email, and SMS channels.
- **Singleton Database & Config:** Centralized application and session management.
- **Comprehensive Testing:** >=80% test coverage with `pytest`, `pytest-mock`, and headless Chrome `selenium` E2E suites.

---

## 🏗️ Architecture & Directory Structure

```text
ClinicCare/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Singleton configuration
│   ├── extensions.py         # SQLAlchemy & DB session manager
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py           # User, PatientProfile, DoctorProfile
│   │   ├── department.py     # Clinic departments
│   │   ├── appointment.py    # Availability & Appointment lifecycle
│   │   ├── billing.py        # Invoice & Payment records
│   │   └── notification.py   # Notification & Outbox logging
│   ├── patterns/             # Gang of Four (GoF) Design Patterns
│   │   ├── singleton.py      # AppConfig & SessionManager
│   │   ├── factory.py        # NotificationFactory (InApp, Email, SMS)
│   │   ├── adapter.py        # PaymentGatewayAdapter (Card, MobileWallet)
│   │   ├── strategy.py       # DiscountStrategy (Senior, Student, Promo)
│   │   └── observer.py       # AppointmentEventObserver (Notify, Invoice, Audit)
│   ├── routes/               # Flask Blueprints
│   │   ├── public.py         # Landing, Doctor directory & details
│   │   ├── auth.py           # Authentication & RBAC guards
│   │   ├── patient.py        # Patient appointments, invoices, profile
│   │   ├── doctor.py         # Doctor schedule & visit notes
│   │   ├── billing.py        # Invoice payment & printable receipts
│   │   ├── admin.py          # Clinic management & revenue reports
│   │   └── api.py            # Optional REST API (/api/v1)
│   ├── templates/            # Jinja2 medical templates
│   └── static/               # CSS styles and JavaScript
├── docs/                     # Engineering documentation
│   ├── requirements.md       # Functional & non-functional requirements
│   ├── process-model.md      # Agile (Scrum-Lite) sprint plan
│   ├── patterns.md           # Design pattern explanations & trade-offs
│   ├── new-tool.md           # Self-learned tool: GitHub Actions vs Jenkins
│   ├── test-report.md        # Test suite & coverage documentation
│   ├── viva-notes.md         # Viva voce questions, answers & architecture
│   ├── report-outline.md     # Submission pack mapping
│   ├── reflection-essay-draft.md # Personal reflection essay
│   ├── merge-conflict-note.md# Merge conflict demonstration report
│   ├── mockups/              # HTML wireframes
│   └── uml/                  # UML class & sequence diagrams
├── tests/
│   ├── conftest.py           # Pytest fixtures and test clients
│   ├── unit/                 # Unit tests for patterns and models
│   └── e2e/                  # Headless Chrome Selenium tests
├── seed.py                   # Demo database seeding script
├── requirements.txt          # Production and testing dependencies
├── WORKLOG.md                # Chronological development activity log
└── AI_USAGE.md               # AI assistance tracking disclosure
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.11+
- Git & GitHub CLI (`gh`)
- Google Chrome (for Selenium E2E tests)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/ibtee12/ClinicCare.git
cd ClinicCare

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Demo Data
```bash
python seed.py
```

### 3. Run Development Server
```bash
flask run --port 5000
```
Open your browser at `http://127.0.0.1:5000`.

---

## 👥 Demo Credentials

| Role | Email | Password | Details |
|---|---|---|---|
| **Admin** | `admin@cliniccare.test` | `Admin123!` | System administrator with full reporting |
| **Doctor** | `dr.farhan@cliniccare.test` | `Doctor123!` | Cardiology Consultant (Fee: 800 BDT) |
| **Doctor** | `dr.nusrat@cliniccare.test` | `Doctor123!` | Dermatology Specialist (Fee: 600 BDT) |
| **Patient (Senior)** | `rahim@patient.test` | `Patient123!` | Age 65 (Eligible for 20% Senior Citizen discount) |
| **Patient (Student)** | `anika@patient.test` | `Patient123!` | Age 21, Verified Student (15% discount) |
| **Patient (Standard)**| `karim@patient.test` | `Patient123!` | First visit eligible (10% discount) |

---

## 🧪 Testing

Execute unit and integration tests with coverage report:
```bash
pytest --cov=app --cov-report=term-missing tests/unit
```

Run Headless Selenium End-to-End tests:
```bash
pytest tests/e2e
```

Run Code Style Linting:
```bash
flake8 app tests
```
