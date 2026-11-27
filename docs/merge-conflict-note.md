# Merge Conflict Demonstration & Resolution Note

**Course:** RUET CSE 3206 Software Engineering Sessional  
**Author:** 2203004  
**Date:** November 27, 2026  
**Branches Involved:** `feature/conflict-branch-a` (PR #32) vs `feature/conflict-branch-b` (PR #33)  

---

## 1. Conflict Description & Context

To satisfy the engineering curriculum requirement demonstrating real Git version control conflict handling, a deliberate concurrent modification was created on the core system configuration file `app/config.py`:

- **Branch A (`feature/conflict-branch-a`):** Defined `DEFAULT_SLOT_MINUTES = 20` for rapid outpatient consultations.
- **Branch B (`feature/conflict-branch-b`):** Defined `DEFAULT_SLOT_MINUTES = 45` for extended diagnostic reviews.

Branch A was reviewed and merged into `main` via PR #32. When attempting to merge `main` back into Branch B, Git flagged a content conflict:

```text
Auto-merging app/config.py
CONFLICT (content): Merge conflict in app/config.py
Automatic merge failed; fix conflicts and then commit the result.
```

---

## 2. Raw Git Conflict Markers

```python
"""Global configuration and clinic operational parameters."""

<<<<<<< HEAD
DEFAULT_SLOT_MINUTES = 45  # Extended comprehensive consultation track (Option B)
=======
DEFAULT_SLOT_MINUTES = 20  # Fast consultation track (Option A)
>>>>>>> origin/main
MAX_BOOKING_DAYS_AHEAD = 60
CANCELLATION_MINIMUM_HOURS = 2
```

---

## 3. Engineering Resolution Strategy

Rather than naively discarding one branch's proposal, we resolved the conflict by synthesizing a balanced, production-standard configuration:
- Set `DEFAULT_SLOT_MINUTES = 30` as the standard baseline consultation interval.
- Exposed explicit configurations for both rapid (`RAPID_SLOT_MINUTES = 20`) and extended (`EXTENDED_SLOT_MINUTES = 45`) tracks.
- Verified all unit and E2E regression test suites before committing and pushing the resolution.

---

## 4. Post-Resolution Clean Code

```python
"""Global configuration and clinic operational parameters."""

# Standard balanced consultation slot duration
DEFAULT_SLOT_MINUTES = 30

# Optional specialty consultation duration tiers
RAPID_SLOT_MINUTES = 20
EXTENDED_SLOT_MINUTES = 45

MAX_BOOKING_DAYS_AHEAD = 60
CANCELLATION_MINIMUM_HOURS = 2
```
