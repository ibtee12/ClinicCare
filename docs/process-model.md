# Software Process Model: Agile (Scrum-Lite)

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Project:** ClinicCare Web Application  

---

## 1. Process Model Selection & Justification

For the development of **ClinicCare**, the **Agile (Scrum-Lite)** methodology has been chosen over the traditional Waterfall or heavy Rational Unified Process (RUP). 

### Justification:
1. **Iterative & Incremental Delivery:** The clinic platform consists of tightly integrated modules (Auth, Patients, Doctors, Appointments, Billing, Notifications). Delivering the system in distinct, testable increments ensures that core domain entities (Users, Doctors, Appointments) are fully verified before building dependent layers (Billing and Notifications).
2. **Rapid Feedback & TDD Alignment:** Test-Driven Development (TDD) demands an iterative cycle: writing failing unit tests, implementing minimal working code, and refactoring. Scrum sprints provide natural boundaries for this cycle.
3. **Change Adaptability & Risk Mitigation:** Complex business rules—such as dynamic discount evaluation (Strategy pattern) and multi-channel notification dispatching (Factory + Observer patterns)—benefit from phased verification. If an interface changes, only the current sprint's increment is affected.

---

## 2. Sprint & Increment Plan

The project is structured into **5 sequential sprints / increments**, mapping directly to the project milestones:

```
+---------------------------------------------------------------------------------+
| Sprint 1: Foundation & Scaffold                                                 |
| - Requirements engineering, user stories, wireframes, repository architecture   |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
| Sprint 2: Core Design Patterns Architecture                                     |
| - Factory (Notifications), Singleton (Config/DB), Adapter (Payments),           |
|   Strategy (Discounts), Observer (Appointment Lifecycle Events)                 |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
| Sprint 3: Core Domain Modules Implementation (TDD)                              |
| - Auth, Patient Profiles, Doctor Scheduling, Appointments, Billing, Admin       |
| - Mocked database and external payment/SMS services, seed data, >=80% coverage  |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
| Sprint 4: End-to-End Verification & CI/CD Pipeline                              |
| - Headless Chrome Selenium automation, GitHub Actions workflow, coverage badges |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
| Sprint 5: Hardening, Conflict Resolution Exercise & Release Packaging          |
| - Deliberate merge conflict resolution, v1.0.0 release, viva notes & report     |
+---------------------------------------------------------------------------------+
```

### Sprint Breakdown Table

| Sprint | Goal | Key Deliverables | Estimated Story Points |
|---|---|---|:---:|
| **Sprint 1** | Inception & Blueprint | Requirements doc, 16 User Stories, Mockups, Architecture scaffold, Git workflow setup | 8 |
| **Sprint 2** | Design Patterns Engine | 5 GoF patterns implemented via TDD; UML class diagram; Code review audit trail | 13 |
| **Sprint 3** | Business Modules & UI | Auth, Patients, Doctors, Appointments, Billing, Admin dashboards, responsive templates, seed data | 21 |
| **Sprint 4** | E2E Testing & CI/CD | Headless Selenium suite, GitHub Actions CI workflow, `new-tool.md` (GH Actions vs Jenkins) | 13 |
| **Sprint 5** | Production Readiness | Deliberate merge conflict resolution, v1.0.0 GitHub release, viva defense notes, final audit | 8 |

---

## 3. Quality Assurance & Definition of Done (DoD)

Each user story and feature branch must satisfy the following **Definition of Done**:
1. Branch created from latest `main` using standard naming (`feature/*`, `fix/*`, `docs/*`).
2. Unit tests written first (TDD) demonstrating failure, followed by implementation passing the test.
3. Test suite executed locally with `pytest --cov` achieving >= 80% coverage.
4. Clean code verification via `flake8` with no syntax or PEP8 errors.
5. Pull Request opened against `main` referencing user story issue (`Closes #n`).
6. Genuine code review comment recorded in PR.
7. Merged cleanly using merge commit (`--no-ff`), keeping linear and verifiable git history.
8. Real development progress and technical decisions recorded in `WORKLOG.md` and `AI_USAGE.md`.
