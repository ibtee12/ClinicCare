# ClinicCare - AI Usage Attribution & Audit Log

**Project:** ClinicCare Clinic Appointment and Billing Web Application  
**Course:** RUET CSE 3206 Software Engineering Sessional  
**Academic Year:** 2026  
**Student ID:** 2203004  

---

## 1. Overview and Engineering Ethics Statement

In compliance with RUET academic integrity and software engineering sessional guidelines, this document explicitly records all interactions, prompts, and architectural artifacts developed with the assistance of the AI autonomous engineering agent (Antigravity). All architectural decisions, design pattern structures, business rules, and test cases were validated, executed, and verified through real git version control commits, pull requests, automated unit tests, and browser E2E suites.

---

## 2. Granular AI Collaboration Log

| Step / Component | Prompt Summary | AI-Generated Artifacts | Human/Agent Review & Verification |
| :--- | :--- | :--- | :--- |
| **Step 1: Scaffold & Requirements** | "Build, test, version and ship ClinicCare. Create requirements, process model, HTML mockups, scaffold, and GitHub issues." | `docs/requirements.md`<br>`docs/process-model.md`<br>`docs/mockups/*.html`<br>16 GitHub Issues | Verified against RUET CSE 3206 specification; mapped 16 user stories to sprint increments. |
| **Step 2: GoF Design Patterns** | "Implement 5 GoF patterns in TDD style. Push one incomplete PR, review and reject it, then submit complete PR." | `app/patterns/singleton.py`<br>`app/patterns/strategy.py`<br>`app/patterns/adapter.py`<br>`app/patterns/observer.py`<br>`app/patterns/factory.py`<br>`docs/patterns.md`<br>`docs/uml/class_diagram.mmd` | Conducted rigorous code review on PR #19; rejected unmerged. Merged revised PR #20 with non-stacking discount strategy. |
| **Step 3: Core Modules & Seed** | "Implement Auth, Patients, Doctors, Appointments, Billing, Admin, Notifications, REST API, and seed script." | `app/models/*`<br>`app/routes/*`<br>`app/templates/*`<br>`seed.py`<br>`tests/unit/*`<br>`docs/test-report.md` | Enforced strict PEP8 compliance (<=79 chars); verified 54 passing unit tests and 82% code coverage. |
| **Step 4: Selenium & CI/CD** | "Add Selenium E2E headless Chrome tests, GitHub Actions CI workflow, and new tool study." | `tests/e2e/test_selenium_flow.py`<br>`.github/workflows/ci.yml`<br>`docs/new-tool.md`<br>`LEARNING_LOG.md` | Fixed template assertion matching in live server fixture; verified 4 E2E tests passing headless. |
| **Step 5: Conflict & Submission** | "Simulate deliberate merge conflict, resolve it, create v1.0.0 release, and author report outline, viva notes, and essay." | `app/config.py`<br>`docs/merge-conflict-note.md`<br>`docs/report-outline.md`<br>`docs/viva-notes.md`<br>`docs/reflection-essay-draft.md` | Verified merge conflict markers in git; resolved with clean unified slot tiers. |

---

## 3. Toolchain & AI Environment Details
- **Agent Platform:** Antigravity (Google DeepMind)
- **Underlying Engine:** Gemini
- **CLI & Execution Tools:** `git`, `gh` (GitHub CLI v2.83.0), `pytest`, `flake8`, `selenium`
