# Unified Grading System - Complete Guide

## 📋 Overview

The **Unified Grading System** (`unified_grader.py`) provides a structured menu interface for managing both:
- **ATM Banking System** (PHP) - Milestone-based grading
- **Laravel Event Management** - Rubric-based grading

This system combines the best features from `menu.py` (structured workflow) and extends it to support Laravel projects.

---

## 🎯 Features

### Common Features
- ✅ Structured menu navigation
- ✅ Real-time command output
- ✅ Clear status messages
- ✅ Confirmation prompts for critical operations
- ✅ Error handling and validation

### ATM Banking System
- ✅ Grade all students (milestone-based)
- ✅ Upload grades to Moodle
- ✅ Send Teams messages
- ✅ Verify email mappings
- ✅ View student summary

### Laravel Event Management
- ✅ Grade all students (use existing repos)
- ✅ Grade all students (pull latest changes)
- ✅ Upload grades to Moodle
- ✅ Send Teams notifications
- ✅ View student summary

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+** installed
2. **Required packages** installed:
   ```powershell
   pip install gitpython pygithub openai requests
   ```

3. **Configuration file** (`config.py`) properly set up:
   - GitHub credentials
   - Moodle credentials (optional)
   - Repository prefixes
   - Student email mappings

4. **Teams Webhook** (optional):
   ```powershell
   $env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/YOUR_URL"
   ```

### Running the System

```powershell
python unified_grader.py
```

---

## 📖 Menu Structure

```
UNIFIED AUTO-GRADING SYSTEM
├── [1] ATM Banking System
│   ├── [1] Grade All Students
│   ├── [2] Upload Grades to Moodle
│   ├── [3] Send Teams Messages
│   ├── [4] Verify Email Mappings
│   ├── [5] View Student Summary
│   └── [6] Back to Main Menu
│
├── [2] Laravel Event Management
│   ├── [1] Grade All Students (use existing repos)
│   ├── [2] Grade All Students (pull latest changes)
│   ├── [3] Upload Grades to Moodle
│   ├── [4] Send Teams Notifications
│   ├── [5] View Student Summary
│   └── [6] Back to Main Menu
│
├── [3] View Grading Reports
├── [4] Compare Student Performance
├── [5] View Configuration
└── [6] Exit
```

---

## 🔧 Workflows

### ATM Banking System Workflow

```
1. Select [1] ATM Banking System
2. Select [1] Grade All Students
   → Runs Main.py
   → Generates result.txt and result.html per student
   → Creates student_summary.txt

3. Select [2] Upload Grades to Moodle
   → Reads student_summary.txt
   → Uploads grades to Moodle
   → Creates moodle_grade_log.txt

4. Select [3] Send Teams Messages
   → Reads grading results
   → Sends individual messages via Teams webhook
   → Logs sent messages
```

### Laravel Event Management Workflow

```
1. Select [2] Laravel Event Management
2. Select [1] Grade All Students (use existing repos)
   → Runs Laravel_grader.py (no pull)
   → Finds Laravel projects recursively
   → Generates grading_result.json and result.html per student
   → Uses existing cloned repositories

   OR

   Select [2] Grade All Students (pull latest changes)
   → Runs Laravel_grader.py --update
   → Pulls latest changes from GitHub first
   → Then grades all students

3. Select [3] Upload Grades to Moodle
   → Reads grading_result.json files
   → Calculates scores
   → Uploads to Moodle using LARAVEL_MOODLE_* configuration
   → Creates upload log

4. Select [4] Send Teams Notifications
   → Reads grading results
   → Sends adaptive cards to Teams
   → Includes score, grade, and report link
```

---

## 📊 Grading Systems

### ATM Banking System (Milestone-based)

**Total: 100 points**

| Category | Points |
|----------|--------|
| Basic Setup & Core Features | 25 |
| Security & Validation | 20 |
| Transaction Features | 25 |
| Advanced Features | 15 |
| Admin & Logging | 10 |
| Additional Security | 5 |

**Scoring:**
- Each milestone has weighted points
- Points awarded based on file existence and code features
- AI-powered review provides additional feedback
- Bonuses for instruction following and quality code
- Penalties for late submissions

### Laravel Event Management (Rubric-based)

**Total: 100 points**

#### With Functionality Tests (115 points scaled to 100):
| Category | Points |
|----------|--------|
| Models | 15 |
| Controllers | 15 |
| Migrations | 10 |
| Routes | 8 |
| Views | 8 |
| Constraint Logic | 10 |
| Documentation | 8 |
| Commits | 10 |
| Functionality Tests | 30 |

#### Without Tests (115 points scaled to 100):
| Category | Points |
|----------|--------|
| Models | 20 |
| Controllers | 20 |
| Migrations | 15 |
| Routes | 10 |
| Views | 10 |
| Constraint Logic | 15 |
| Documentation | 10 |
| Commits | 15 |

**Scoring:**
- Static analysis checks for keywords and patterns
- Optional PHPUnit test execution (if PHP/Composer available)
- Proportional scoring (71/115 = 62/100)
- AI-powered review for comprehensive feedback
- Detects Blade, Vue, React, Svelte views

---

## 🔔 Notifications

### Teams Notifications

**ATM Banking System:**
- Plain text messages with scores
- Includes repository name and grade
- Sent after grading completes

**Laravel Event Management:**
- Adaptive card format with color coding
- Green (A): 90-100
- Blue (B): 80-89
- Yellow (C): 70-79
- Orange (D): 60-69
- Red (F): 0-59
- Includes link to HTML report

### Moodle Integration

**Both Systems:**
- Looks up student by GitHub username
- Uploads score (0-100) to gradebook
- Uses appropriate course/activity/grade item IDs
- Logs uploads for verification

---

## ⚙️ Configuration

### config.py Structure

```python
# GitHub Configuration
GITHUB_TOKEN = "your_token"
ORG_NAME = "your_org"

# ATM Banking System
ASSIGNMENT_REPO_PREFIX = "midterm-exam-atm-"
ATM_MOODLE_COURSE_ID = 123
ATM_MOODLE_ACTIVITY_ID = 456
ATM_MOODLE_GRADE_ITEM_ID = 789

# Laravel Event Management
LARAVEL_ASSIGNMENT_REPO_PREFIX = "event-scheduler-"
LARAVEL_MOODLE_COURSE_ID = 123
LARAVEL_MOODLE_ACTIVITY_ID = 789
LARAVEL_MOODLE_GRADE_ITEM_ID = 101

# Moodle Integration
MOODLE_URL = "https://your-moodle-site.com"
MOODLE_TOKEN = "your_token"

# Other Settings
OUTPUT_DIR = "cloned_repos"
SUBMISSION_DEADLINE = "2025-11-15 23:59:59"
FREEZE_GRADING = False
```

### Environment Variables

```powershell
# Teams Webhook (optional)
$env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/..."
```

---

## 🐛 Troubleshooting

### "No grading results found"
**Cause:** Grading hasn't been run yet
**Fix:** Select option [1] to grade students first

### "TEAMS_WEBHOOK_URL not set"
**Cause:** Environment variable not configured
**Fix:** 
```powershell
$env:TEAMS_WEBHOOK_URL = "your_webhook_url"
```

### "Moodle credentials not configured"
**Cause:** MOODLE_URL or MOODLE_TOKEN not set in config.py
**Fix:** Edit config.py and add Moodle credentials

### "Could not import Laravel_grader"
**Cause:** Laravel_grader.py not in the same directory
**Fix:** Ensure Laravel_grader.py exists in project root

### "Could not import Main"
**Cause:** Main.py not in the same directory
**Fix:** Ensure Main.py exists in project root

### "Student not found in Moodle"
**Cause:** GitHub username doesn't match Moodle username
**Fix:** Check student mapping in STUDENT_EMAILS in config.py

---

## 📝 Output Files

### ATM Banking System

```
cloned_repos/
├── midterm-exam-atm-student1/
│   ├── result.txt          # Plain text grading report
│   └── result.html         # HTML grading report
├── midterm-exam-atm-student2/
│   └── ...
├── student_summary.txt     # Summary of all students
└── moodle_grade_log.txt    # Moodle upload log
```

### Laravel Event Management

```
cloned_repos/
├── event-scheduler-student1/
│   ├── grading_result.json # Detailed JSON results
│   └── result.html         # HTML grading report
├── event-scheduler-student2/
│   └── ...
└── moodle_update_results.txt # Moodle upload log
```

---

## 🎓 Best Practices

1. **Always grade first** before uploading or sending notifications
2. **Review results** in the summary view before uploading to Moodle
3. **Use existing repos** option for Laravel to save time
4. **Pull latest changes** only when you know students have updated
5. **Test with one student** before running batch operations
6. **Check webhook URL** is set before sending Teams notifications
7. **Verify Moodle configuration** before uploading grades
8. **Keep backups** of student_summary.txt and grading results

---

## 🔄 Comparison with Other Tools

| Tool | Purpose | Use When |
|------|---------|----------|
| `unified_grader.py` | Combined menu interface | Managing both project types |
| `menu.py` | ATM system only | Only grading ATM projects |
| `Main.py` | Direct ATM grading | Running ATM grader directly |
| `Laravel_grader.py` | Direct Laravel grading | Running Laravel grader directly |

---

## 🚀 Quick Reference

### Grade ATM Students
```
unified_grader.py → [1] → [1]
```

### Grade Laravel Students (No Pull)
```
unified_grader.py → [2] → [1]
```

### Grade Laravel Students (With Pull)
```
unified_grader.py → [2] → [2]
```

### Upload to Moodle (ATM)
```
unified_grader.py → [1] → [2]
```

### Upload to Moodle (Laravel)
```
unified_grader.py → [2] → [3]
```

### Send Teams Notifications (ATM)
```
unified_grader.py → [1] → [3]
```

### Send Teams Notifications (Laravel)
```
unified_grader.py → [2] → [4]
```

---

## ✅ Checklist for Complete Grading Session

### ATM Banking System
- [ ] Run unified_grader.py
- [ ] Select [1] ATM Banking System
- [ ] Select [1] Grade All Students
- [ ] Review results in [5] View Student Summary
- [ ] Select [2] Upload Grades to Moodle
- [ ] Select [3] Send Teams Messages
- [ ] Verify in Moodle gradebook

### Laravel Event Management
- [ ] Run unified_grader.py
- [ ] Select [2] Laravel Event Management
- [ ] Select [1] or [2] to grade (with/without pull)
- [ ] Review results in [5] View Student Summary
- [ ] Select [3] Upload Grades to Moodle
- [ ] Select [4] Send Teams Notifications
- [ ] Verify in Moodle gradebook and Teams channel

---

**System Complete! All grading operations now have a structured, user-friendly interface.** 🎉
