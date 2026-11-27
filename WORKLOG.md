# Chronological Engineering Worklog

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Project:** ClinicCare Web Application  
**Author / Git Identity:** `ibtee12` (`2203004@student.ruet.ac.bd`)  

---

## [2026-11-27] Phase 1: Environment Setup, Requirements & Blueprinting

### Activities Completed:
1. **Environment Discovery & Toolchain Verification:**
   - Checked operating system: macOS arm64.
   - Verified Python 3.11 installation.
   - Identified that GitHub CLI (`gh`) was initially missing from PATH. Installed `gh` via Homebrew (`brew install gh`).
   - Retrieved authenticated GitHub token from macOS Keychain (`security find-internet-password`).
   - Configured `~/.config/gh/hosts.yml` with token scopes `read:user`, `repo`, `user:email`, `workflow`. Verified connection to `ibtee12/ClinicCare`.
   - Setup Python 3.11 virtual environment (`.venv`) and installed dependencies: `Flask`, `Flask-SQLAlchemy`, `Werkzeug`, `pytest`, `pytest-mock`, `pytest-cov`, `selenium`, `webdriver-manager`, `flake8`, `python-dotenv`.
   - Confirmed presence of Google Chrome at `/Applications/Google Chrome.app`.

2. **Step 1 Scaffolding:**
   - Created Git branch `docs/requirements-and-process`.
   - Created `.gitignore` ignoring `.venv`, `__pycache__`, SQLite files, `.pytest_cache`, `.coverage`, etc.
   - Pinned dependencies in `requirements.txt`.
   - Authored `docs/requirements.md` including executive summary, RBAC matrix, functional requirements (FR), non-functional requirements (NFR), 16 user stories with acceptance criteria, and detailed use cases (UC-01, UC-02).
   - Authored `docs/process-model.md` detailing the Agile (Scrum-Lite) methodology and a 5-sprint increment plan.
   - Designed 6 HTML wireframe mockups in `docs/mockups/`:
     - `landing.html` (hero, departments, featured doctors, how it works)
     - `doctor_profile.html` (credentials, visual slot picker)
     - `patient_dashboard.html` (upcoming appointments, notifications, unpaid bills)
     - `booking.html` (slot selection, discount calculation preview)
     - `invoice.html` (printable invoice breakdown)
     - `admin_dashboard.html` (stats cards, doctor management, revenue chart)
   - Created comprehensive `README.md` with features, architecture, setup instructions, and demo credentials.

### Real Errors Encountered & Fixes:
- **Error:** `zsh: command not found: gh`.
  - *Fix:* Executed `brew install gh` via Homebrew in background task.
- **Error:** `gh auth login --with-token` failed with `missing required scope 'read:org'`.
  - *Fix:* Token in keychain had `repo`, `workflow`, `user:email` but not `read:org`. Direct configuration via `~/.config/gh/hosts.yml` bypassed the interactive organization scope check, allowing full repo/workflow/issue/PR management via GitHub CLI.

### Tools Used:
- `zsh`, `brew`, `python3.11`, `pip`, `git`, `gh`.
