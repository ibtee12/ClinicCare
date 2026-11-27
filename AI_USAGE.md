# AI Usage Disclosure Statement

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Project:** ClinicCare Clinic Appointment and Billing Web Application  
**Student Name / Roll:** Nahyan Yasir Ibtee / 2203004  
**Git Identity:** `ibtee12` (`2203004@student.ruet.ac.bd`)  

---

## 1. Overview & Policy Adherence

This document logs all generative AI tool interactions, prompts, and modifications during the design, implementation, and testing of **ClinicCare**. In compliance with RUET academic guidelines and modern software engineering practices, AI is utilized as an autonomous pair programmer and architectural accelerator, while all code, tests, and documentation are rigorously verified, validated through automated test pipelines, and placed under strict version control.

---

## 2. Activity & Prompt Record

| Step / Milestone | Prompt Summary | AI Output / Contribution | Human Review & Modifications |
|---|---|---|---|
| **Step 1: Inception & Scaffold** | "Build, test, version and ship ClinicCare end to end without stopping for approval. Step 1: Requirements, process model, scaffold." | - Generated `docs/requirements.md` (FRs, NFRs, 16 User Stories, Use Cases).<br>- Authored `docs/process-model.md` justifying Agile (Scrum-Lite).<br>- Built 6 HTML wireframes in `docs/mockups/`.<br>- Created project architecture scaffold and requirements. | Verified all 6 modules and 5 GoF patterns are accounted for; validated Bangladeshi phone regex (`01XXXXXXXXX`) and refund rules (24h/2h thresholds). |
| **Step 2: Design Patterns** | "Implement 5 design patterns across 3 categories with TDD, UML diagram, and PR review cycle." | - Generated pattern implementations (Factory, Singleton, Adapter, Strategy, Observer).<br>- Created test suites with failing red-green tests.<br>- Documented pattern trade-offs in `docs/patterns.md`. | Inspected decoupling of payment SDKs and discount calculation to ensure zero discount stacking. |
| **Step 3: Core Modules** | "Implement Auth, Patients, Doctors, Appointments, Billing, Notifications with TDD and mocks; seed.py, >=80% coverage." | - Generated Flask blueprints, SQLAlchemy models, Jinja templates, service classes, and test fixtures using `pytest-mock`. | Verified role decorators prevent unauthorized access with HTTP 403; confirmed slot double-booking prevention. |
| **Step 4: E2E & CI/CD** | "Add Selenium tests, GitHub Actions CI workflow, and new tool documentation." | - Configured `.github/workflows/ci.yml`.<br>- Created headless Chrome Selenium test scenarios.<br>- Authored `docs/new-tool.md` (GitHub Actions vs Jenkins). | Verified headless flags for CI compatibility and verified CI green run. |
| **Step 5: Polish & Pack** | "Execute deliberate merge conflict exercise, create v1.0.0 release, viva notes, reflection essay." | - Executed merge conflict simulation and resolution.<br>- Created viva voce question bank and reflection essay. | Formatted and finalized submission pack. |
