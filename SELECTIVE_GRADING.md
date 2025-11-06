# Selective Grading Guide

## Overview
The selective grading feature allows you to re-grade specific students and control whether to send Teams notifications or upload grades to Moodle. This is useful when you need to:

- Re-grade a student who submitted late or made corrections
- Update documentation scores after README improvements
- Send notifications only to specific students
- Upload grades selectively to Moodle

---

## Usage Methods

### Method 1: Using Unified Grader Menu (Interactive)

```bash
python unified_grader.py
```

1. Select **[2] Laravel Event Management**
2. Select **[3] Grade Specific Students (selective grading)**
3. Enter student usernames (space-separated): `p-e-koko ndrewpk glad1223`
4. Choose options:
   - Pull latest changes? (y/n)
   - Skip Teams notifications? (y/n)
   - Skip Moodle upload? (y/n)
5. Confirm and run

### Method 2: Using Command Line (Direct)

#### Grade specific students only
```bash
python Laravel_grader.py --students p-e-koko ndrewpk
```

#### Re-grade one student with latest code
```bash
python Laravel_grader.py -s glad1223 --update
```

#### Grade but don't send notifications
```bash
python Laravel_grader.py -s p-e-koko --skip-teams --skip-moodle
```

#### Re-grade and send only Teams message (no Moodle upload)
```bash
python Laravel_grader.py -s p-e-koko --update --skip-moodle
```

#### Re-grade and upload only to Moodle (no Teams message)
```bash
python Laravel_grader.py -s ndrewpk glad1223 --skip-teams
```

---

## Command Line Options

### Laravel_grader.py Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--students USERNAME [USERNAME...]` | `-s` | Grade only specified students (GitHub usernames) |
| `--update` | `-u`, `--pull` | Pull latest changes from GitHub before grading |
| `--skip-teams` | - | Skip sending Teams notifications |
| `--skip-moodle` | - | Skip uploading grades to Moodle |

### Student Username Format

Use GitHub usernames **without the repository prefix**:

✅ **Correct**: `p-e-koko`, `ndrewpk`, `glad1223`  
❌ **Wrong**: `event-scheduler-p-e-koko` (includes prefix)

The script automatically prepends the prefix from `config.py`:
- Laravel: `event-scheduler-` → `event-scheduler-p-e-koko`
- ATM: `midterm-exam-atm-` → `midterm-exam-atm-p-e-koko`

---

## Common Scenarios

### Scenario 1: Student Improved README
**Problem**: Student p-e-koko updated their README with better documentation  
**Solution**: Re-grade to update documentation score and send notification

```bash
python Laravel_grader.py -s p-e-koko --update --skip-moodle
```

**Result**: 
- ✅ Pulls latest code (with updated README)
- ✅ Re-grades project (documentation score improves)
- ✅ Sends Teams message with new grade
- ❌ Does NOT upload to Moodle (manual verification first)

### Scenario 2: Late Submission
**Problem**: Student submitted after grading deadline  
**Solution**: Grade their work separately

```bash
python Laravel_grader.py -s glad1223 --skip-teams
```

**Result**:
- ✅ Grades using existing cloned repo
- ✅ Uploads to Moodle
- ❌ Does NOT send Teams message (notify manually after review)

### Scenario 3: Fix Grading Error
**Problem**: Found a bug in grading script, need to re-grade everyone  
**Solution**: Re-grade all, but don't spam notifications

```bash
python Laravel_grader.py --skip-teams --skip-moodle
```

**Result**:
- ✅ Re-grades all students
- ✅ Generates new HTML reports
- ❌ Does NOT send notifications
- ❌ Does NOT upload to Moodle (review first)

### Scenario 4: Multiple Students, Selective Actions
**Problem**: Re-grade 3 students and only send Teams notifications  
**Solution**: Target specific students, skip Moodle

```bash
python Laravel_grader.py -s p-e-koko ndrewpk glad1223 --skip-moodle --update
```

**Result**:
- ✅ Pulls latest for these 3 students
- ✅ Re-grades only these 3 students
- ✅ Sends Teams messages to these 3 students
- ❌ Does NOT upload to Moodle

---

## Verification Steps

### Before Re-grading
1. Check current grade:
   ```bash
   # View current result
   start cloned_repos\event-scheduler-p-e-koko\backend\result.html
   ```

2. Check if repo exists:
   ```bash
   dir cloned_repos\event-scheduler-p-e-koko
   ```

### After Re-grading
1. Compare new vs old grade:
   - Open `result.html` in browser
   - Check each category score
   - Verify documentation score updated

2. Check logs:
   - `teams_grade_log.txt` - Teams messages sent
   - `moodle_grade_log.txt` - Moodle uploads
   - Terminal output for errors

---

## Tips & Best Practices

### ✅ Do's
- ✅ Always use `--skip-moodle` first, review grades, then upload manually
- ✅ Use `--update` when students have pushed new commits
- ✅ Verify result.html before sending notifications
- ✅ Keep logs for audit trail

### ❌ Don'ts
- ❌ Don't re-grade without `--skip-teams` if you're testing the script
- ❌ Don't upload to Moodle multiple times (creates duplicate entries)
- ❌ Don't use repo names as student filter (use GitHub username only)
- ❌ Don't forget to pull (`--update`) if student made changes

### Performance
- Grading 1 student: ~30 seconds
- Grading 3 students: ~90 seconds
- Grading all 16 students: ~8 minutes

---

## Troubleshooting

### "No matching repositories found"
**Problem**: Script can't find student repos  
**Solutions**:
```bash
# Check exact username
python list_students.py

# Verify prefix in config.py
python show_config.py

# Use correct username (not repo name)
python Laravel_grader.py -s p-e-koko  # ✅ Correct
python Laravel_grader.py -s event-scheduler-p-e-koko  # ❌ Wrong
```

### Teams notification fails
**Problem**: Teams message not sent  
**Solutions**:
- Check `STUDENT_EMAILS` in config.py
- Verify student email is mapped correctly
- Re-authenticate if token expired
- Check `teams_grade_log.txt` for errors

### Moodle upload fails
**Problem**: Grade not uploaded to Moodle  
**Solutions**:
- Verify `LARAVEL_MOODLE_*` settings in config.py
- Check Moodle token is valid
- Ensure student exists in Moodle course
- Check `moodle_grade_log.txt` for errors

---

## Examples Output

### Successful Selective Grading
```
[FILTER] Grading only 1 student(s): p-e-koko
======================================================================
Grading event-scheduler-p-e-koko...
======================================================================
[EXISTS] Repository already cloned, pulling latest changes...
[UPDATED] Successfully pulled latest changes
[SEARCHING] Looking for Laravel project in: cloned_repos\event-scheduler-p-e-koko
[FOUND] Laravel project at: cloned_repos\event-scheduler-p-e-koko\backend

[GRADING] Using rubric: WITHOUT functionality tests
[INFO] Maximum possible points: 115

[RESULT] Final Score: 68/100
[SAVED] JSON report: cloned_repos\event-scheduler-p-e-koko\backend\grading_result.json
[SAVED] HTML report: cloned_repos\event-scheduler-p-e-koko\backend\result.html

[NOTIFICATION] Sending notifications for p-e-koko...
[TEAMS] ✓ Message sent to 202300203@my.apiu.edu

[SKIP] Moodle upload skipped for p-e-koko
======================================================================
Grading complete!
======================================================================
```

---

## Quick Reference Card

```bash
# Re-grade one student (most common)
python Laravel_grader.py -s USERNAME --update

# Re-grade multiple students
python Laravel_grader.py -s USER1 USER2 USER3

# Grade without notifications (for testing)
python Laravel_grader.py -s USERNAME --skip-teams --skip-moodle

# Send only Teams (after reviewing grade)
python Laravel_grader.py -s USERNAME --skip-moodle

# Upload only to Moodle (after confirming grade)
python Laravel_grader.py -s USERNAME --skip-teams

# Full re-grade with all actions
python Laravel_grader.py -s USERNAME --update
```

---

## Integration with Unified Grader

The unified grader menu provides an interactive way to use selective grading:

1. Launch: `python unified_grader.py`
2. Navigate: `[2] Laravel → [3] Grade Specific Students`
3. Input: Enter usernames and choose options
4. Review: Check result.html files
5. Confirm: Upload to Moodle or send Teams manually if needed

This method is recommended for users who prefer GUI-style interaction over command-line arguments.
