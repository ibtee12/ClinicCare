# ClinicCare - System Requirements Specification

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Project:** ClinicCare — Clinic Appointment and Billing Web Application  
**Technology Stack:** Python 3.11, Flask, SQLAlchemy + SQLite, Jinja2, HTML5/CSS3, pytest, pytest-mock, pytest-cov, Selenium, GitHub Actions  

---

## 1. Executive Summary & Purpose

ClinicCare is an integrated, single-clinic web application engineered to streamline patient appointment scheduling, doctor availability management, consultation billing with simulated payments, and event-driven notifications. It provides role-based access control (RBAC) across three distinct user roles: **Patient**, **Doctor**, and **Clinic Administrator**.

---

## 2. Roles and Permissions Matrix

| Feature / Action | Guest | Patient | Doctor | Admin |
|---|:---:|:---:|:---:|:---:|
| View Landing Page, Doctors List, Doctor Profile | ✅ | ✅ | ✅ | ✅ |
| Register as Patient / Login | ✅ | ✅ | ✅ | ✅ |
| Manage Patient Profile & Medical History | ❌ | ✅ | ❌ | ❌ |
| Book / Reschedule / Cancel Own Appointments | ❌ | ✅ | ❌ | ❌ |
| View Own Invoices & Make Online Payments | ❌ | ✅ | ❌ | ❌ |
| View In-App Notifications | ❌ | ✅ | ✅ | ✅ |
| Configure Weekly Availability Slots | ❌ | ❌ | ✅ | ❌ |
| View Doctor Dashboard & Update Visit Status / Notes | ❌ | ❌ | ✅ | ❌ |
| Manage Doctors (Create, Edit, Deactivate) | ❌ | ❌ | ❌ | ✅ |
| Manage Medical Departments & Discount Strategies | ❌ | ❌ | ❌ | ✅ |
| View System-Wide Appointments & Revenue Reports | ❌ | ❌ | ❌ | ✅ |

Every protected route enforces strict Role-Based Access Control via custom Python decorators (`@login_required`, `@role_required`). Unauthorized requests return HTTP 403 with user-friendly error guidance.

---

## 3. Functional Requirements (FR)

### Module 1: Authentication & Authorization
- **FR-AUTH-01:** System shall permit new patients to register with name, email, password, and phone number.
- **FR-AUTH-02:** System shall securely hash passwords using Werkzeug (`generate_password_hash` with scrypt/pbkdf2).
- **FR-AUTH-03:** System shall authenticate users and maintain secure session states.
- **FR-AUTH-04:** System shall restrict endpoints based on user role (`patient`, `doctor`, `admin`).
- **FR-AUTH-05:** System shall permit authenticated users to update their passwords.

### Module 2: Patients Management
- **FR-PAT-01:** Patients can view and update their profile (age, gender, phone, address, blood group, student status).
- **FR-PAT-02:** Patients can view their medical history and visit history summary.
- **FR-PAT-03:** Phone numbers must strictly conform to Bangladeshi format (`01XXXXXXXXX`).

### Module 3: Doctors & Departments
- **FR-DOC-01:** Doctors belong to medical departments (e.g., General Medicine, Cardiology, Pediatrics, Dermatology).
- **FR-DOC-02:** Public directory allows filtering doctors by department and searching by doctor name.
- **FR-DOC-03:** Doctors configure weekly availability rules (weekday 0-6, start time, end time, slot length in minutes).
- **FR-DOC-04:** System dynamically generates bookable, discrete time slots from availability rules.

### Module 4: Appointment Scheduling Lifecycle
- **FR-APT-01:** Patients can select a doctor and date to view available time slots.
- **FR-APT-02:** Prevents double-booking: a doctor slot can have at most one active (non-cancelled) appointment.
- **FR-APT-03:** Booking must be for future dates within a 60-day window.
- **FR-APT-04:** Appointments follow strict state lifecycle: `PENDING` -> `CONFIRMED` -> `COMPLETED`, or `CANCELLED` / `NO_SHOW`.
- **FR-APT-05:** Patients can cancel appointments at least 2 hours before the scheduled start time. Cancellations under 2 hours are forbidden.
- **FR-APT-06:** Patients can reschedule appointments to another available slot up to 2 hours before start.

### Module 5: Billing & Simulated Payments
- **FR-BIL-01:** An invoice is automatically generated upon appointment booking with base fee, applied discount, and total payable amount.
- **FR-BIL-02:** System calculates applicable discounts using the Strategy pattern:
  - `NoDiscount`: 0%
  - `SeniorCitizen`: 20% discount if patient age >= 60
  - `Student`: 15% discount if profile has student flag
  - `FirstVisit`: 10% discount if patient has zero prior completed/confirmed appointments
  - `PromoCode`: customizable percentage code (e.g., `RUET2026` = 10%)
  - *Rule:* Best single discount applies; discounts never stack.
- **FR-BIL-03:** Payments processed via simulated Payment Gateway Adapters (Credit/Debit Card Adapter and Mobile Wallet Adapter like bKash/Nagad).
- **FR-BIL-04:** Payment statuses: `UNPAID`, `PAID`, `REFUNDED`, `FAILED`.
- **FR-BIL-05:** Cancellation refund policy:
  - Cancelled >= 24 hours prior: 100% full refund.
  - Cancelled between 2 and 24 hours prior: 50% partial refund.
  - Cancelled < 2 hours prior: Not allowed (0% refund).
- **FR-BIL-06:** Invoices have a clean, printable HTML view.

### Module 6: Notifications & Audit Logging
- **FR-NOT-01:** System dispatches notifications upon booking, confirmation, payment, and cancellation via Factory pattern (`InApp`, `Email`, `SMS`).
- **FR-NOT-02:** Email and SMS notifications are logged to simulated outbox storage.
- **FR-NOT-03:** In-app notifications are visible in the user's dashboard and can be marked as read.

### Module 7: Administration & Reporting
- **FR-ADM-01:** Admin dashboard displays total patients, total doctors, today's appointments, and total clinic revenue.
- **FR-ADM-02:** Admin can add new doctors, assign departments, set fees, and deactivate/activate accounts.
- **FR-ADM-03:** Admin can manage departments and view all appointments filtered by date, doctor, or status.
- **FR-ADM-04:** Admin can view monthly revenue breakdown and doctor revenue distribution with visual charts.

---

## 4. Non-Functional Requirements (NFR)

- **NFR-01 (Performance):** Average page response time < 1.0 second on seed data under local execution.
- **NFR-02 (Security):** Secure password hashing using Werkzeug; role guards on every endpoint; CSRF token validation on forms; SQL injection immunity through SQLAlchemy ORM parameterization.
- **NFR-03 (Reliability & Persistence):** SQLite database persistence with relational foreign keys and transaction rollbacks on failure.
- **NFR-04 (Testability & Code Coverage):** Automated unit and mock test suite targeting >= 80% line coverage via `pytest-cov`.
- **NFR-05 (Code Quality):** Code passes `flake8` PEP8 linting standards without critical violations.
- **NFR-06 (Portability):** Configurable via environment variables with zero proprietary system dependencies. Runs cleanly on Python 3.11 on Linux/macOS/Windows.
- **NFR-07 (Extensibility):** Design patterns (Strategy, Adapter, Observer, Factory, Singleton) ensure new payment methods, discounts, and notification channels require only a single class and registry entry without modifying core business loops.

---

## 5. User Stories & Acceptance Criteria

### Patient Stories
1. **US-01 (Registration):** *As a new patient*, I want to create an account with my basic details so that I can schedule clinic appointments.
   - *Acceptance Criteria:* Validates Bangladeshi phone (`01XXXXXXXXX`), valid email format, password >= 8 characters.
2. **US-02 (Doctor Search):** *As a patient*, I want to search and filter doctors by department and name so that I can find the right specialist.
   - *Acceptance Criteria:* Publicly accessible; shows qualifications, consultation fee, and bio.
3. **US-03 (Book Appointment):** *As a patient*, I want to pick an available date and time slot so that I can book an appointment.
   - *Acceptance Criteria:* Only unbooked future slots within 60 days are selectable. An invoice is immediately created in `UNPAID` status.
4. **US-04 (Apply Discount):** *As a patient*, I want the system to calculate the best eligible discount (senior, student, first-visit, promo) so that my bill is accurate.
   - *Acceptance Criteria:* Applies highest single discount rate; prevents stacking.
5. **US-05 (Pay Bill):** *As a patient*, I want to pay my consultation invoice via Card or Mobile Wallet (bKash) so that my appointment is confirmed.
   - *Acceptance Criteria:* Simulated gateway processes transaction; updates invoice and appointment status to `PAID`/`CONFIRMED`.
6. **US-06 (Cancel Appointment):** *As a patient*, I want to cancel my appointment if plans change and receive an automated refund based on clinic policy.
   - *Acceptance Criteria:* Blocked within 2 hours of slot; 100% refund if >= 24h before; 50% refund if 2-24h before.
7. **US-07 (Reschedule Appointment):** *As a patient*, I want to reschedule my appointment to a different slot up to 2 hours before the start.
   - *Acceptance Criteria:* Updates slot time without duplicating invoice; notifies doctor.
8. **US-08 (View Medical & Visit History):** *As a patient*, I want to view my past visits, doctor notes, and prescriptions.
   - *Acceptance Criteria:* Read-only access to completed visits and attached visit notes.

### Doctor Stories
9. **US-09 (Availability Setup):** *As a doctor*, I want to configure my weekly schedule by weekday, start/end hours, and slot duration so that patients can only book when I am available.
   - *Acceptance Criteria:* Slots generated cleanly based on defined start/end and minute increments.
10. **US-10 (Manage Daily Schedule):** *As a doctor*, I want to view my appointments for today and upcoming dates.
    - *Acceptance Criteria:* Filterable by date; shows patient name, age, phone, and reason for visit.
11. **US-11 (Record Visit Notes):** *As a doctor*, I want to mark an appointment as `COMPLETED` and add visit notes and prescription advice.
    - *Acceptance Criteria:* Saves doctor notes; triggers completion notification to patient.
12. **US-12 (Mark No-Show):** *As a doctor*, I want to mark an absent patient as `NO_SHOW` to close out the appointment.
    - *Acceptance Criteria:* Status updates to `NO_SHOW`; slot released from active queue.

### Administrator Stories
13. **US-13 (Manage Doctors):** *As an admin*, I want to register doctors, assign their departments, and manage their status.
    - *Acceptance Criteria:* Admin can create doctor credentials, set consultation fee, and deactivate doctor accounts.
14. **US-14 (Manage Departments):** *As an admin*, I want to create and organize clinical departments.
    - *Acceptance Criteria:* CRUD operations on clinic departments.
15. **US-15 (Appointment Overview):** *As an admin*, I want to view all clinic appointments across doctors and filter by date/status.
    - *Acceptance Criteria:* Tabular overview with search and filter capabilities.
16. **US-16 (Revenue & Financial Reports):** *As an admin*, I want to view revenue reports grouped by doctor and month with charts so that I can monitor clinic financial performance.
    - *Acceptance Criteria:* Displays aggregated revenue metrics and HTML5/Canvas visual charts.

---

## 6. Key Use Cases

### UC-01: Book Appointment & Generate Invoice
- **Primary Actor:** Patient
- **Preconditions:** Patient is logged in; target doctor has configured availability slots.
- **Main Flow:**
  1. Patient navigates to doctor's profile page and clicks "Book Appointment".
  2. Patient selects a date (within 1 to 60 days from now).
  3. System renders available, unbooked slots for that doctor on that weekday.
  4. Patient selects a slot, inputs reason for visit, and optional promo code.
  5. System executes Discount Strategy to identify maximum applicable discount.
  6. System creates Appointment (`PENDING`) and Invoice (`UNPAID`).
  7. Observer triggers `NotificationObserver` to log booking notification to Patient.
  8. Patient is redirected to `/pay/<invoice_id>`.

### UC-02: Cancel Appointment with Automated Refund
- **Primary Actor:** Patient
- **Preconditions:** Appointment is `CONFIRMED` or `PENDING`, and invoice has been paid.
- **Main Flow:**
  1. Patient views appointment list and clicks "Cancel Appointment".
  2. System checks time delta: `time_to_start = appointment.start_datetime - now()`.
  3. If `time_to_start < 2 hours`: System rejects cancellation with 400 Bad Request error.
  4. If `time_to_start >= 24 hours`: Refund percentage = 100%.
  5. If `2 hours <= time_to_start < 24 hours`: Refund percentage = 50%.
  6. Appointment status is set to `CANCELLED`.
  7. Invoice status is set to `REFUNDED` (or updated with refund transaction record).
  8. Observers fire: Patient and Doctor receive cancellation notifications; Audit log records the action.
