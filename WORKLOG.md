# ClinicCare - Engineering Worklog

All entries represent actual development steps, errors encountered, and resolutions achieved during the RUET CSE 3206 Software Engineering Sessional.

---

### Step 1: Requirements, Process Model, & Project Scaffold
- **Branch:** `docs/requirements-and-process` (Merged via PR #17)
- **Actions:**
  - Authored `docs/requirements.md` detailing functional and non-functional requirements, 16 user stories (`US-01` through `US-16`), and use cases.
  - Authored `docs/process-model.md` justifying the Agile Scrum-Lite process model and mapping sprints to the 6 system modules.
  - Created 6 responsive HTML wireframes in `docs/mockups/`.
  - Configured project directory structure (`app/`, `tests/`, `docs/`).
  - Created 16 corresponding GitHub Issues (#1 through #16) using GitHub CLI (`gh issue create`).

---

### Step 2: Object-Oriented Design Patterns (TDD)
- **Singleton Pattern:** (Merged via PR #18)
  - Implemented `AppConfig` and `DatabaseSessionManager` in `app/patterns/singleton.py` using thread-safe metaclass locks. Tested with 4 passing unit tests.
- **Strategy Pattern & Review Cycle:** (PR #19 closed unmerged; Merged via PR #20)
  - Submitted deliberately incomplete strategy branch in PR #19 with hardcoded discount rules and tight coupling.
  - Performed code review via `gh pr review --comment` detailing 4 critical design flaws; closed PR unmerged.
  - Opened revised branch `feature/strategy-discount-complete` implementing `NoDiscount`, `SeniorCitizenDiscount`, `StudentDiscount`, `FirstVisitDiscount`, and `PromoCodeDiscount` with `select_best_discount()`. Verified with 8 unit tests in PR #20.
- **Adapter Pattern:** (Merged via PR #21)
  - Created `PaymentGateway` target interface adapting `CardGatewayAdapter` and `MobileWalletAdapter` with decline and timeout handling. Verified with 6 unit tests.
- **Observer Pattern:** (Merged via PR #22)
  - Implemented event subject dispatching status updates to `NotificationObserver`, `InvoiceObserver`, and `AuditLogObserver`. Verified with 3 unit tests.
- **Factory Pattern:** (Merged via PR #23)
  - Implemented `NotificationFactory` creating `InAppNotifier`, `EmailNotifier`, and `SmsNotifier` with dynamic channel registry. Verified with 5 unit tests.
- **Pattern Documentation & UML:** (Merged via PR #24)
  - Documented pattern solutions and rejected alternatives in `docs/patterns.md`. Visualized class structures in `docs/uml/class_diagram.mmd`.

---

### Step 3: Core Application Modules with TDD & Mocks
- **Module 1 (Auth):** (Merged via PR #25)
  - Implemented User ORM model, Werkzeug PBKDF2 hashing, session management, and `@role_required` RBAC decorator with 403 page.
- **Module 2 (Patients):** (Merged via PR #26)
  - Implemented `PatientProfile` model, demographic editing, patient dashboard, and medical history views.
- **Module 3 (Doctors):** (Merged via PR #27)
  - Built doctor directory, specialty filters, doctor dashboard, weekly schedule editor, and `slot_service.py`.
- **Module 4 (Appointments):** (Merged via PR #28)
  - Implemented booking workflow with 60-day advance window, double-booking prevention, 2-hour cancellation rule, and status transitions.
- **Module 5 (Billing & Invoices):** (Merged via PR #29)
  - Implemented invoice generation, discount calculation, payment adapter checkout, and printable invoice views.
- **Module 6 (Admin, Notifications & REST API):** (Merged via PR #30)
  - Built clinic administration dashboard, doctor rostering/toggling, departmental management, revenue reports, in-app notifications, and `/api/v1` endpoints.
  - Authored `seed.py` with 1 admin, 6 doctors, 4 departments, 10 patients (senior 65 & student), and 15 appointments.
  - Created `docs/test-report.md` verifying 54 unit tests passing with 82% coverage.

---

### Step 4: Headless Selenium E2E Suite, CI/CD, & Tool Study
- **Branch:** `ci/selenium-actions-pipeline` (Merged via PR #31)
- **Actions:**
  - Implemented headless Chrome E2E tests in `tests/e2e/test_selenium_flow.py` using Selenium WebDriver and background test server daemon.
  - Created `.github/workflows/ci.yml` running flake8 linting, unit tests with coverage, headless Chrome E2E suite, and database seed verification.
  - Authored `docs/new-tool.md` conducting trade-off study between GitHub Actions and Jenkins.
  - Documented technical learnings in `LEARNING_LOG.md`.

---

### Step 5: Deliberate Merge Conflict & Final Submission Pack
- **Conflict Branches:** `feature/conflict-branch-a` (PR #32) & `feature/conflict-branch-b` (PR #33)
- **Conflict Handling:**
  - Branch A modified `app/config.py` to set 20-minute slots; merged via PR #32.
  - Branch B modified `app/config.py` to set 45-minute slots; triggered Git merge conflict.
  - Conflict markers resolved manually by standardizing 30-minute default and exposing tiered slot constants.
  - Documented in `docs/merge-conflict-note.md` and merged via PR #33.
- **Submission Pack:**
  - Authored `docs/report-outline.md`, `docs/viva-notes.md`, and `docs/reflection-essay-draft.md`.
  - Created GitHub Release `v1.0.0`.
