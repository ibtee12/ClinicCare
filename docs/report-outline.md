# ClinicCare - Sessional Report Outline

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Academic Year:** 2026  
**Repository:** [https://github.com/ibtee12/ClinicCare](https://github.com/ibtee12/ClinicCare)  
**Student Name / Roll:** 2203004  

---

## 1. Project Overview & Motivation
- **Clinical Problem:** Overburdened clinics face appointment double-booking, scheduling confusion, opaque billing, and manual notification bottlenecks.
- **ClinicCare Solution:** An end-to-end, lightweight medical appointment and automated billing system built using Python 3.11, Flask, SQLAlchemy, Jinja2, and SQLite.
- **Roles & Permissions:** Role-Based Access Control (RBAC) across three distinct actors: Patient, Doctor, and Clinic Administrator.

---

## 2. Software Engineering Process Model
- **Process Chosen:** Agile (Scrum-Lite) with 4 structured increments.
- **Requirements Traceability:** 16 User Stories (`US-01` through `US-16`) documented in `docs/requirements.md` and tracked as individual GitHub Issues (`#1` to `#16`).
- **Wireframes:** 6 responsive HTML mockups located in `docs/mockups/` covering Landing, Doctor Search, Patient Dashboard, Appointment Booking, Printable Invoices, and Admin Analytics.

---

## 3. Object-Oriented Architecture & GoF Design Patterns
Detailed in `docs/patterns.md` and visualised in `docs/uml/class_diagram.mmd`:
1. **Singleton Pattern (Creational):** Thread-safe configuration manager (`AppConfig`) and database session coordinator (`DatabaseSessionManager`).
2. **Factory Pattern (Creational):** Multi-channel notification delivery (`NotificationFactory` spawning `InAppNotifier`, `EmailNotifier`, `SmsNotifier`).
3. **Adapter Pattern (Structural):** Standardized gateway interface (`PaymentGateway`) adapting card (`CardGatewayAdapter`) and mobile wallet (`MobileWalletAdapter`) SDKs.
4. **Strategy Pattern (Behavioral):** Non-stacking discount calculations (`SeniorCitizenDiscount`, `StudentDiscount`, `FirstVisitDiscount`, `PromoCodeDiscount`, `NoDiscount`).
5. **Observer Pattern (Behavioral):** Event-driven appointment lifecycle dispatching (`AppointmentSubject` triggering `NotificationObserver`, `InvoiceObserver`, `AuditLogObserver`).

---

## 4. Modules & Implementation Details
- **Module 1: Authentication & Authorization:** PBKDF2:SHA256 password hashing, session guards, and HTTP 403 error handler.
- **Module 2: Patient Portal:** Profile management, demographic tracking, and medical history.
- **Module 3: Doctor Rostering & Directory:** Specialty filtering, weekly availability matrices, and dynamic slot calculation.
- **Module 4: Appointment Scheduling:** 60-day advance window, double-booking prevention, 2-hour cancellation threshold.
- **Module 5: Billing & Payments:** Invoicing engine, discount strategy selection, payment simulation, and tiered refund logic (100% $\ge 24$h, 50% 2–24h).
- **Module 6: Admin Portal & System Notifications:** Clinic analytics dashboard, doctor toggling, departmental management, revenue reports, and REST API (`/api/v1`).

---

## 5. Quality Assurance, Testing & CI/CD
- **TDD Methodology:** Failing unit tests (`test:`) committed before implementations (`feat:`).
- **Unit Testing:** 54 test cases passing in `pytest` with `pytest-mock` isolating payment gateways and SQLite.
- **Code Coverage:** **82%** statement coverage verified by `pytest-cov` (detailed in `docs/test-report.md`).
- **End-to-End Automation:** Headless Chrome browser automation with `Selenium` (`tests/e2e/test_selenium_flow.py`).
- **Continuous Integration:** Cloud-native pipeline via `.github/workflows/ci.yml` running linting, coverage, E2E tests, and seed verification.
- **Comparative Study:** In-depth evaluation of GitHub Actions vs. Jenkins documented in `docs/new-tool.md`.

---

## 6. Version Control & Collaborative Engineering Evidence
- **Branching Policy:** Strict non-master branching (`feature/*`, `fix/*`, `ci/*`, `docs/*`).
- **Review Cycle Evidence:** Closed PR #19 unmerged after rigorous review comments, replaced by clean PR #20.
- **Merge Conflict Resolution:** Deliberate concurrent modification resolved in `app/config.py` and documented in `docs/merge-conflict-note.md`.
- **Release Versioning:** Tagged Semantic Version `v1.0.0` on GitHub.
