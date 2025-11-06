# Unified Grading System - Complete Guide

## ✅ What Was Added

### Laravel Grader Features:

1. **Teams Notifications** - Sends a message card to Microsoft Teams after each student is graded
2. **Moodle Grade Upload** - Automatically uploads grades to Moodle gradebook
3. **Immediate Notifications** - Sends notifications right after each student's grading completes
4. **Repository Management** - Skip re-downloading existing repos (use `--update` to pull changes)

### Unified Grader (unified_grader.py):

1. **Structured Menu System** - Similar to menu.py, with organized options
2. **ATM Banking System Menu** - Grade, upload to Moodle, send Teams messages
3. **Laravel Event Management Menu** - Grade (with/without update), upload, notify
4. **Separate workflows** - Each project type has dedicated operations

---

## 🔧 Setup Instructions

### 1. Microsoft Teams Webhook Setup

**Step 1: Create Incoming Webhook in Teams**

1. Open Microsoft Teams
2. Go to the channel where you want notifications
3. Click **...** (More options) → **Connectors** → **Incoming Webhook**
4. Click **Configure**
5. Give it a name: "Laravel Grader Bot"
6. Upload an icon (optional)
7. Click **Create**
8. **Copy the webhook URL** (looks like: `https://outlook.office.com/webhook/...`)

**Step 2: Set Environment Variable**

**Windows (PowerShell):**
```powershell
# Set for current session
$env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL_HERE"

# Set permanently (recommended)
[System.Environment]::SetEnvironmentVariable('TEAMS_WEBHOOK_URL', 'https://outlook.office.com/webhook/YOUR_WEBHOOK_URL_HERE', 'User')
```

**Windows (Command Prompt):**
```cmd
setx TEAMS_WEBHOOK_URL "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL_HERE"
```

**Verify it's set:**
```powershell
$env:TEAMS_WEBHOOK_URL
```

---

### 2. Moodle Integration Setup

Moodle integration uses your existing `MoodleIntegration.py` and configuration.

**Verify Configuration (config.py):**

```python
# Moodle Configuration
MOODLE_URL = "https://your-moodle-site.com"
MOODLE_TOKEN = "your_moodle_token_here"

# Laravel Assignment Configuration
LARAVEL_MOODLE_COURSE_ID = 123  # Your course ID
LARAVEL_MOODLE_ACTIVITY_ID = 456  # Assignment activity ID
LARAVEL_MOODLE_GRADE_ITEM_ID = 789  # Grade item ID
```

**If not configured yet:**

1. Open `config.py`
2. Add the Laravel assignment configuration
3. Get values from Moodle:
   - Course ID: URL when viewing course
   - Activity ID: Assignment page URL
   - Grade Item ID: From gradebook settings

---

## 📊 How It Works

### Workflow After Integration:

```
For Each Student:
  1. Clone/pull repository
  2. Find Laravel project
  3. Run tests (if available)
  4. Run static analysis
  5. Calculate score
  6. Generate result.html
  7. ⭐ Send Teams notification
  8. ⭐ Upload grade to Moodle
  9. Move to next student
```

---

## 📧 Teams Notification Format

Students will see a card like this in Teams:

```
🌟 Laravel Project Graded - studentname

Student:      studentname
Repository:   event-scheduler-studentname
Score:        85/100
Grade:        B
Graded on:    2025-11-06 14:30:45

[View Report] (clickable link)
```

**Color coding:**
- 🌟 Green (A): 90-100
- 👍 Blue (B): 80-89
- ⚠️ Yellow (C): 70-79
- 📝 Orange (D): 60-69
- ❌ Red (F): 0-59

---

## 🎓 Moodle Grade Upload

The grader will:

1. Look up student by GitHub username
2. Upload score (0-100) to Moodle gradebook
3. Log the upload to `moodle_grade_log.txt`

**Log format:**
```
2025-11-06 14:30:45 | studentname | event-scheduler-studentname | 85/100
2025-11-06 14:31:12 | student2 | event-scheduler-student2 | 92/100
```

---

## 🔍 Testing

### Test Teams Notification

```powershell
# Set webhook URL
$env:TEAMS_WEBHOOK_URL = "your_webhook_url"

# Run grader on one student
python Laravel_grader.py
```

You should see:
```
[NOTIFICATION] Sending notifications for studentname...
[TEAMS] ✓ Notification sent to Teams for studentname
[MOODLE] ✓ Grade uploaded successfully
```

### Test Without Teams/Moodle

If not configured, you'll see:
```
[SKIP] Teams webhook not configured (set TEAMS_WEBHOOK_URL environment variable)
[SKIP] Moodle not configured
```

The grading will continue normally without notifications.

---

## ⚙️ Configuration Options

### Disable Teams Notifications

```powershell
# Remove environment variable
Remove-Item Env:TEAMS_WEBHOOK_URL
```

### Disable Moodle Upload

Edit `config.py`:
```python
MOODLE_URL = None  # Set to None to disable
```

### Change Notification Timing

Currently sends **immediately after each student**. To change to batch mode:

1. Store results in a list during grading loop
2. Send all notifications after loop completes

---

## 📝 Console Output Example

```
======================================================================
Grading event-scheduler-student1...
======================================================================
[EXISTS] Repository already cloned, pulling latest changes...
[FOUND] Laravel project at: cloned_repos\event-scheduler-student1\app

[GRADING] Using rubric: WITHOUT functionality tests
[RESULT] Final Score: 85/100
[SAVED] JSON report: cloned_repos\event-scheduler-student1\app\grading_result.json
[SAVED] HTML report: cloned_repos\event-scheduler-student1\app\result.html

[NOTIFICATION] Sending notifications for student1...
[TEAMS] ✓ Notification sent to Teams for student1
[MOODLE] Looking up student: student1
[MOODLE] Uploading grade 85/100 for student1...
[MOODLE] ✓ Grade uploaded successfully

======================================================================
Grading event-scheduler-student2...
======================================================================
...
```

---

## 🐛 Troubleshooting

### "Teams webhook not configured"
- **Cause:** Environment variable not set
- **Fix:** Set `TEAMS_WEBHOOK_URL` as shown above

### "Failed to send notification: 400"
- **Cause:** Invalid webhook URL or message format
- **Fix:** Re-create webhook in Teams, copy new URL

### "Student not found in Moodle"
- **Cause:** GitHub username doesn't match Moodle username
- **Fix:** Check username mapping in Moodle

### "MoodleIntegration module not available"
- **Cause:** MoodleIntegration.py not in same directory
- **Fix:** Ensure MoodleIntegration.py exists in project root

### Webhook expires
- **Cause:** Teams webhooks can expire if unused
- **Fix:** Create new webhook, update environment variable

---

## 🚀 Quick Start

### Option 1: Using Unified Grader (Recommended)

```powershell
# Run the unified grading system
python unified_grader.py

# Then select:
# [2] Laravel Event Management
# [1] Grade All Students (use existing repos)
# [4] Send Teams Notifications (after grading)
# [3] Upload Grades to Moodle (after grading)
```

### Option 2: Direct Laravel Grader

**Minimum setup to get notifications:**

```powershell
# 1. Set Teams webhook
$env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/YOUR_URL"

# 2. Run grader (uses existing repos, no re-download)
python Laravel_grader.py

# Done! Students will be notified in Teams (if configured in Laravel_grader.py main loop)
```

**Full setup (Teams + Moodle):**

```powershell
# 1. Set Teams webhook
$env:TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/YOUR_URL"

# 2. Configure Moodle in config.py
# (Edit MOODLE_URL, MOODLE_TOKEN, LARAVEL_MOODLE_* variables)

# 3. Run grader (uses existing repos, no re-download)
python Laravel_grader.py

# Done! Students notified in Teams + grades in Moodle
```

**Update existing repos before grading:**

```powershell
# Pull latest changes from GitHub before grading
python Laravel_grader.py --update

# Or use short form
python Laravel_grader.py -u
```

**Note:** By default, the script **does not re-download** existing repositories. It only clones new ones. Use `--update` to pull the latest changes from GitHub.

---

## ✅ Verification Checklist

- [ ] Teams webhook created and URL copied
- [ ] Environment variable `TEAMS_WEBHOOK_URL` set
- [ ] Moodle credentials in `config.py`
- [ ] Moodle course/activity IDs configured
- [ ] `MoodleIntegration.py` exists
- [ ] Test run on one student successful
- [ ] Teams message received
- [ ] Grade appears in Moodle

---

## 📋 Next Steps

1. **Set up Teams webhook** (5 minutes)
2. **Configure Moodle** (if not already done)
3. **Test on one student**
4. **Run full grading** on all students
5. **Verify notifications** and grades

---

**Integration Complete! Students will now receive immediate feedback via Teams, and grades will automatically sync to Moodle.** 🎉
