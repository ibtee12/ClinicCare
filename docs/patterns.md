# Design Patterns in ClinicCare

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Project:** ClinicCare Web Application  
**Author:** `ibtee12` (`2203004@student.ruet.ac.bd`)  

---

## Overview

ClinicCare implements **5 Gang of Four (GoF) design patterns** spanning all **three design categories**: **Creational**, **Structural**, and **Behavioral**. Each pattern was implemented using Test-Driven Development (TDD) to promote modularity, testability, and adherence to SOLID design principles.

---

## 1. Creational Patterns

### 1.1 Singleton Pattern (`AppConfig` & `DatabaseSessionManager`)
- **Category:** Creational
- **Location:** `app/patterns/singleton.py`, `tests/unit/test_singleton.py`
- **Problem Solved:**  
  ClinicCare requires central configuration parameters (such as `CANCELLATION_FULL_REFUND_HOURS = 24`, `CANCELLATION_MIN_HOURS = 2`, `MAX_BOOKING_DAYS_AHEAD = 60`, promo codes, and secret keys) as well as consistent database session scoping. Without a singleton, disparate modules instantiate multiple config instances or open uncoordinated database sessions, creating concurrency race conditions and configuration divergence.
- **Implementation Highlights:**  
  Uses `SingletonMeta` with **double-checked locking** using `threading.Lock()` to ensure complete thread-safety across concurrent web requests.
- **Rejected Alternative & Rationale:**  
  *Rejected:* Global dictionary or raw module-level variables.  
  *Why Rejected:* Global variables lack thread-safe initialization, prevent dynamic test environment overrides, cannot be scoped cleanly, and expose mutable state without access encapsulation.

---

### 1.2 Factory Method Pattern (`NotificationFactory`)
- **Category:** Creational
- **Location:** `app/patterns/factory.py`, `tests/unit/test_factory.py`
- **Problem Solved:**  
  Notifications must be dispatched across multiple distinct delivery channels: **In-App alerts** (stored in DB for patient/doctor dashboard), **Email** (written to simulated SMTP outbox), and **SMS** (formatted for Bangladeshi mobile numbers `01XXXXXXXXX`). Creating these dispatchers directly in business routes tightly couples controller logic to concrete notification transports.
- **Implementation Highlights:**  
  `NotificationFactory.create(channel)` instantiates and returns a concrete `BaseNotifier` (`InAppNotifier`, `EmailNotifier`, `SMSNotifier`). Supports open-ended extension via `NotificationFactory.register(channel, cls)`.
- **Rejected Alternative & Rationale:**  
  *Rejected:* Hardcoded `switch`/`if-elif` channel dispatching scattered inside appointment controllers.  
  *Why Rejected:* Violates the Open/Closed Principle (OCP). Adding a new channel (e.g., Push Notification or WhatsApp) would require modifying every appointment status handler across the codebase instead of adding a single registered class.

---

## 2. Structural Patterns

### 2.1 Adapter Pattern (`PaymentGatewayAdapter`)
- **Category:** Structural
- **Location:** `app/patterns/adapter.py`, `tests/unit/test_adapter.py`
- **Problem Solved:**  
  The clinic accepts consultation payments through two fundamentally incompatible fake SDKs:
  1. `LegacyCardProcessorSdk`: Requires card number, expiration month/year, CVV, and amounts in integer cents; returns a JSON response dict `{"status": "APPROVED" | "DECLINED" | "TIMEOUT"}`.
  2. `LegacyMobileWalletSdk`: Designed like bKash/Nagad; requires an MSISDN phone string, BDT amount, and PIN; returns a raw tuple `(success_bool, tx_id, error_code)`.
- **Implementation Highlights:**  
  Defines a uniform `PaymentGateway` interface with method `process_payment(amount, payment_data) -> PaymentResult`.  
  - `CardGatewayAdapter` maps dollars to cents, extracts card fields, and translates timeout responses to `retryable = True`.  
  - `MobileWalletAdapter` validates mobile format, executes mobile wallet transactions, and returns standardized `PaymentResult` instances.
- **Rejected Alternative & Rationale:**  
  *Rejected:* Directly calling `LegacyCardProcessorSdk` and `LegacyMobileWalletSdk` inside `app/routes/billing.py` with custom conditionals.  
  *Why Rejected:* Pollutes controller routes with gateway-specific data transformations, makes unit testing with mocks exceedingly brittle, and breaks the Single Responsibility Principle.

---

## 3. Behavioral Patterns

### 3.1 Strategy Pattern (`DiscountStrategy`)
- **Category:** Behavioral
- **Location:** `app/patterns/strategy.py`, `tests/unit/test_strategy.py`
- **Problem Solved:**  
  ClinicCare supports diverse discount rules:
  - `SeniorCitizen`: 20% discount for patients aged 60+.
  - `Student`: 15% discount for verified student patients.
  - `FirstVisit`: 10% discount for first-time clinic attendees.
  - `PromoCode`: Configurable coupon codes (e.g., `RUET2026` = 10%).  
  *Strict Rule:* Only the **best single discount** applies—discounts must **never stack**.
- **Implementation Highlights:**  
  `DiscountStrategy` base interface with concrete subclasses (`NoDiscountStrategy`, `SeniorCitizenDiscountStrategy`, `StudentDiscountStrategy`, `FirstVisitDiscountStrategy`, `PromoCodeStrategy`).  
  `select_best_discount(base_fee, patient_info)` evaluates all applicable strategies and selects the maximum discount amount without stacking.
- **Rejected Alternative & Rationale:**  
  *Rejected:* Giant procedural `if/elif/else` block inside the appointment creation route.  
  *Why Rejected:* Hard to test boundary edge cases independently, prone to accidental discount stacking bugs, and violates OCP whenever the clinic management introduces seasonal promotions.

---

### 3.2 Observer Pattern (`AppointmentSubject` & Observers)
- **Category:** Behavioral
- **Location:** `app/patterns/observer.py`, `tests/unit/test_observer.py`
- **Problem Solved:**  
  When an appointment changes state (`PENDING` -> `CONFIRMED` -> `COMPLETED`, or `CANCELLED`), multiple independent subsystems must take action:
  1. Patients and doctors must receive state notifications.
  2. If cancelled, the billing subsystem must calculate refunds based on clinic timing rules (100% refund for cancellation >=24h before; 50% refund for 2-24h; 0% for <2h).
  3. The audit log must record a compliance entry.
- **Implementation Highlights:**  
  `AppointmentSubject` maintains registered `AppointmentObserver` instances. When `subject.notify(event)` is fired:
  - `NotificationObserver` formats and queues appropriate messages.
  - `InvoiceObserver` determines refund eligibility and calculates exact refund amounts.
  - `AuditLogObserver` logs immutable timestamped event entries.
- **Rejected Alternative & Rationale:**  
  *Rejected:* Direct synchronous sequential calls in the controller (e.g. `send_sms(); calculate_refund(); write_audit_log();`).  
  *Why Rejected:* High coupling; if notification dispatch fails or changes, it can crash the appointment cancellation transaction. Observers allow asynchronous decoupling and clean test isolation.

---

## Summary Matrix

| Pattern | Category | Key Class / Interface | Solves |
|---|---|---|---|
| **Singleton** | Creational | `SingletonMeta`, `AppConfig`, `DatabaseSessionManager` | Centralized, thread-safe configuration and DB session scope. |
| **Factory** | Creational | `NotificationFactory`, `BaseNotifier` | Decoupled creation of In-App, Email, and SMS dispatchers. |
| **Adapter** | Structural | `PaymentGateway`, `CardGatewayAdapter`, `MobileWalletAdapter` | Unified payment interface over incompatible Card & Mobile SDKs. |
| **Strategy** | Behavioral | `DiscountStrategy`, `select_best_discount` | Dynamic evaluation of best single discount without stacking. |
| **Observer** | Behavioral | `AppointmentSubject`, `AppointmentObserver` | Event-driven notification, refund calculation, and audit logging. |
