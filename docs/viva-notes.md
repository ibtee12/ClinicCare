# ClinicCare - Viva Defense & Technical Q&A Guide

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Target Audience:** Examiner / Viva Board & Student Defense Preparation  
**Student ID:** 2203004  

---

## Part 1: Architecture & Module Explanations

### 1. Application Layering & Separation of Concerns
ClinicCare is architected around an extensible modular structure:
- `app/models/`: SQLAlchemy 2.0 ORM domain entities ensuring relational integrity, foreign keys, and indexes.
- `app/routes/`: Distinct Flask blueprints separating route handling, request validation, and view rendering.
- `app/patterns/`: Standalone GoF design pattern implementations completely decoupled from HTTP frameworks.
- `app/services/`: Pure business logic calculations (such as appointment time-slot generation).
- `app/templates/`: Semantic HTML5 templates utilizing Jinja2 template inheritance and responsive CSS.

### 2. Role-Based Access Control (RBAC)
Security is enforced using Python decorators:
- `@login_required`: Restricts endpoints to authenticated active sessions.
- `@role_required(*allowed_roles)`: Inspects `session.get('role')`. If unauthorized, it terminates execution and aborts with HTTP 403, rendering a user-friendly error template (`app/templates/errors/403.html`).

---

## Part 2: 15 Core Technical Viva Questions & Model Answers

### Q1: Why did you choose SQLite and SQLAlchemy instead of raw SQL queries?
**Answer:** SQLAlchemy ORM maps Python objects to relational tables, providing clean abstraction, automatic SQL parameterization that prevents SQL injection attacks, and declarative schema migrations. SQLite was selected because it is serverless, zero-configuration, embeds directly into memory for ultra-fast unit testing, and is standard for academic project demonstrations.

### Q2: Explain how you implemented the Singleton pattern and how thread safety is guaranteed.
**Answer:** In `app/patterns/singleton.py`, we implemented `SingletonMeta` using Python's metaclass mechanism. Thread safety is guaranteed by wrapping instance creation inside a reentrant lock (`threading.Lock()`). If two threads attempt to initialize `AppConfig` or `DatabaseSessionManager` simultaneously, only one acquires the lock while the second receives the cached instance.

### Q3: What is the Strategy pattern in your project and why not use an `if/else` ladder?
**Answer:** The Strategy pattern is used for consultation discount calculations (`SeniorCitizenDiscount`, `StudentDiscount`, `FirstVisitDiscount`, `PromoCodeDiscount`). An `if/else` chain violates the Open/Closed Principle (OCP); adding a new discount rule would require modifying existing monolithic functions, introducing regression risk. With Strategy, adding a new promotion requires creating an isolated class inheriting from `DiscountStrategy` and adding it to `select_best_discount()`.

### Q4: How does your discount engine prevent discount stacking?
**Answer:** `select_best_discount(patient, base_fee, promo_code)` instantiates all registered discount strategies, calculates the computed monetary reduction for each independently, and returns only the single maximum discount.

### Q5: Explain the Adapter pattern in the billing module.
**Answer:** Different financial institutions provide incompatible payment SDKs (e.g. Visa/Mastercard credit card gateways vs. bKash mobile wallets). The Adapter pattern defines a unified `PaymentGateway` target interface with a `process_payment(amount, reference)` method. `CardGatewayAdapter` and `MobileWalletAdapter` wrap legacy external APIs into this common interface, allowing the checkout service to process transactions polymorphically.

### Q6: How does the Observer pattern decouple appointment status changes from side effects?
**Answer:** When an appointment transitions from `PENDING` to `CONFIRMED` or `CANCELLED`, multiple secondary tasks must occur: sending in-app/SMS notifications, recalculating invoices, and recording audit logs. By using `AppointmentSubject` and registering `NotificationObserver`, `InvoiceObserver`, and `AuditLogObserver`, the core appointment service is completely decoupled from notification delivery or accounting details.

### Q7: How does your application prevent double-booking of doctor appointments?
**Answer:** During slot generation and checkout confirmation:
1. `slot_service.py` queries all non-cancelled appointments for that doctor on the selected date and filters them out.
2. At the database transaction boundary, a query checks `Appointment.query.filter_by(doctor_id=..., start_datetime=..., status!='CANCELLED')`. If an appointment already exists, the transaction is rejected and the user is notified.

### Q8: What are your appointment cancellation and refund business rules?
**Answer:**
- Cancellation is strictly prohibited within 2 hours of the scheduled start time (`start_datetime - now < 2 hours`).
- If cancelled 24+ hours in advance: 100% refund is issued.
- If cancelled between 2 and 24 hours in advance: 50% partial refund is issued.
- The `InvoiceObserver` automatically updates the invoice status to `REFUNDED` and writes an audit entry.

### Q9: How did you implement Test-Driven Development (TDD) in Git?
**Answer:** For every feature, the unit test was written and committed first with the commit prefix `test:` demonstrating a failing assertion. The corresponding implementation was written to satisfy the test, followed by a `feat:` commit, and finally cleanups with `refactor:`.

### Q10: Why did you push an incomplete PR and reject it during the review cycle?
**Answer:** To simulate real-world peer code review dynamics. In PR #19, an incomplete implementation of the Strategy pattern was submitted containing tight coupling and missing edge-case tests. A comprehensive code review comment was posted detailing 4 concrete architectural flaws. PR #19 was closed unmerged, and a revised branch was opened (PR #20) fixing all review findings before being merged.

### Q11: How do you mock external dependencies in unit tests?
**Answer:** We used `pytest-mock` to isolate external boundaries. For instance, in `tests/unit/test_billing.py`, we mock the underlying `CardService.charge()` and `bKashAPI.send_money()` functions to simulate gateway success, decline, and network timeouts without executing real HTTP requests.

### Q12: Why did you select GitHub Actions over Jenkins in your CI/CD study?
**Answer:** As detailed in `docs/new-tool.md`, GitHub Actions is a managed cloud runner requiring zero on-premise infrastructure maintenance, supports declarative YAML configuration versioned in the repo, integrates natively with PR status checks, and provides pre-installed Google Chrome environments for headless Selenium E2E tests.

### Q13: How did you resolve the deliberate merge conflict?
**Answer:** In `app/config.py`, two concurrent branches modified `DEFAULT_SLOT_MINUTES` to 20 and 45 minutes respectively. During the merge, standard Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) appeared. We resolved this by establishing a standard baseline (`DEFAULT_SLOT_MINUTES = 30`) while exposing explicit constants for both rapid and extended tiers, documented in `docs/merge-conflict-note.md`.

### Q14: How is password security managed in ClinicCare?
**Answer:** Passwords are never stored in plaintext. In `app/models/user.py`, `generate_password_hash()` and `check_password_hash()` from `werkzeug.security` are used. These implement salted PBKDF2:SHA256 password hashing with automatic salt generation to prevent rainbow table attacks.

### Q15: How does ClinicCare achieve sub-second response times on seed data?
**Answer:**
1. Database queries are scoped with targeted filters and limits.
2. In-memory SQLite queries execute in sub-millisecond time.
3. Minimal Jinja2 templates without heavy frontend JavaScript frameworks result in minimal DOM parse and render latency (<150ms).
