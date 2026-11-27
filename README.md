# 🏥 ClinicCare - Clinic Appointment & Billing System

[![ClinicCare CI/CD Pipeline](https://github.com/ibtee12/ClinicCare/actions/workflows/ci.yml/badge.svg)](https://github.com/ibtee12/ClinicCare/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-teal.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![Coverage](https://img.shields.io/badge/Coverage-82%25-brightgreen.svg)
![License](https://img.shields.io/badge/License-Academic%20Use-lightgrey.svg)

ClinicCare is a medical clinic appointment and automated billing web application engineered for the **RUET CSE 3206 Software Engineering Sessional**. It features role-based access control, automated time-slot calculation, discount strategy evaluations, payment gateway adapters, event-driven observer updates, in-app notifications, and administrative revenue analytics.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Google Chrome browser (for headless Selenium E2E tests)
- Git & GitHub CLI (`gh`)

### 2. Installation & Setup
```bash
# Clone the repository
git clone https://github.com/ibtee12/ClinicCare.git
cd ClinicCare

# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Seeding
Populate the SQLite database with doctors, departments, patients, appointments, invoices, and payments:
```bash
python seed.py
```

### 4. Running the Web Application
```bash
flask run --port 5000
```
Visit `http://127.0.0.1:5000` in your web browser.

---

## 🔑 Demo Credentials (from `seed.py`)

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@cliniccare.test` | `Admin123!` | Full clinic management, doctors, revenue reports |
| **Doctor** | `house@cliniccare.test` | `Doctor123!` | Dr. Gregory House (Internal Medicine) |
| **Doctor** | `yang@cliniccare.test` | `Doctor123!` | Dr. Cristina Yang (Cardiology) |
| **Doctor** | `robbins@cliniccare.test` | `Doctor123!` | Dr. Arizona Robbins (Pediatrics) |
| **Patient (Senior)** | `alice@patient.test` | `Patient123!` | Age 65 (Receives 20% Senior Citizen discount) |
| **Patient (Student)**| `bob@patient.test` | `Patient123!` | RUET CSE Student (Receives 15% Student discount) |
| **Patient** | `charlie@patient.test`| `Patient123!` | Regular patient (Standard rates / Promo codes) |

---

## 🧪 Testing & Quality Assurance

### Running Unit Tests & Coverage
```bash
pytest --cov=app --cov-report=term-missing tests/unit/
```
*Current Coverage:* **82%** (54 passing unit tests). See [docs/test-report.md](file:///Users/nahyan/Desktop/ClinicCare/docs/test-report.md).

### Running Headless Chrome Selenium E2E Tests
```bash
pytest tests/e2e/test_selenium_flow.py
```

### Linting & PEP8 Compliance
```bash
flake8 app/ tests/ seed.py
```

---

## 🏗️ Architecture & GoF Design Patterns

Detailed documentation available in [docs/patterns.md](file:///Users/nahyan/Desktop/ClinicCare/docs/patterns.md) and [docs/uml/class_diagram.mmd](file:///Users/nahyan/Desktop/ClinicCare/docs/uml/class_diagram.mmd):
1. **Singleton:** Thread-safe `AppConfig` and `DatabaseSessionManager`.
2. **Factory:** `NotificationFactory` creating InApp, Email, and SMS dispatchers.
3. **Adapter:** `PaymentGateway` standardizing Card and Mobile Wallet SDKs.
4. **Strategy:** Best-discount evaluation (`SeniorCitizen`, `Student`, `FirstVisit`, `PromoCode`).
5. **Observer:** `AppointmentSubject` dispatching events to `NotificationObserver`, `InvoiceObserver`, and `AuditLogObserver`.

---

## 📂 Sessional Documentation Index

- [docs/requirements.md](file:///Users/nahyan/Desktop/ClinicCare/docs/requirements.md) - Functional/NFR specifications, 16 User Stories.
- [docs/process-model.md](file:///Users/nahyan/Desktop/ClinicCare/docs/process-model.md) - Agile Scrum-Lite process and sprint allocations.
- [docs/patterns.md](file:///Users/nahyan/Desktop/ClinicCare/docs/patterns.md) - 5 Design patterns, architectural solutions, and rejected alternatives.
- [docs/test-report.md](file:///Users/nahyan/Desktop/ClinicCare/docs/test-report.md) - 82% coverage breakdown across all modules.
- [docs/new-tool.md](file:///Users/nahyan/Desktop/ClinicCare/docs/new-tool.md) - In-depth study: GitHub Actions vs. Jenkins.
- [docs/merge-conflict-note.md](file:///Users/nahyan/Desktop/ClinicCare/docs/merge-conflict-note.md) - Real conflict demonstration and resolution.
- [docs/report-outline.md](file:///Users/nahyan/Desktop/ClinicCare/docs/report-outline.md) - Comprehensive sessional report outline.
- [docs/viva-notes.md](file:///Users/nahyan/Desktop/ClinicCare/docs/viva-notes.md) - Defense preparation with 15 technical Q&As.
- [docs/reflection-essay-draft.md](file:///Users/nahyan/Desktop/ClinicCare/docs/reflection-essay-draft.md) - 500-700 word engineering reflection essay.
- [WORKLOG.md](file:///Users/nahyan/Desktop/ClinicCare/WORKLOG.md) - Dated engineering event log.
- [AI_USAGE.md](file:///Users/nahyan/Desktop/ClinicCare/AI_USAGE.md) - AI collaboration attribution log.
