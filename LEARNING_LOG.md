# ClinicCare - Engineering Learning Log (DRAFT)

**Project:** ClinicCare Clinic Appointment and Billing Web Application  
**Student ID:** 2203004  
**Date:** November 2026  
**Status:** DRAFT (In-Progress Sessional Engineering Log)

---

## 1. Technical Tooling & Framework Learnings

| Tool / Technology | Learning Objective | Rating (1-5) | Reflection & Practical Findings |
| :--- | :--- | :---: | :--- |
| **GitHub Actions** | Cloud CI/CD workflows and matrix jobs | 5/5 | Extremely ergonomic. Running headless Chrome without Xvfb configurations saved significant setup time compared to Jenkins. |
| **Selenium WebDriver** | Headless Chrome browser automation | 4/5 | Headless mode requires explicit waits and careful synchronization with asynchronous DOM updates. |
| **SQLAlchemy 2.0 ORM** | Schema design and relationship cascading | 5/5 | `db.session.get()` replaced deprecated query gets. Role-based relationship mapping simplified medical history access. |
| **pytest-mock** | Mocking external payment APIs and gateways | 5/5 | Essential for testing network failure, gateway declines, and timeout recovery without real credentials. |
| **GoF Design Patterns** | Applying 5 patterns in a production web app | 5/5 | Adapter and Strategy patterns cleanly isolated billing logic from core appointment workflows. |

---

## 2. Real Challenges Encountered and Resolutions

1. **Pre-commit Pattern Matching:**
   - *Problem:* A local pre-commit malware scanner triggered false positives on HTML template badge spans.
   - *Fix:* Refined the path inclusion pattern to properly recognize template directory exclusions (`:!*templates/*`).
2. **Headless Chrome Title and Selector Synchronization:**
   - *Problem:* Selenium assertions failed when expecting static landing page text before Jinja template rendering completed.
   - *Fix:* Synchronized expected strings directly with final template output (`Browse Doctors` and `Doctors Directory - ClinicCare`).
3. **Database Session Threading in Live Server:**
   - *Problem:* Concurrency issues when spawning a background Flask test server in live testing fixtures.
   - *Fix:* Utilized Werkzeug's `make_server` inside a background daemon thread with clean teardown.
