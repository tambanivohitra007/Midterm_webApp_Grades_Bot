# Quick Configuration Reference

## Configuration Variables by Project

### Shared Variables (Used by Both)
```
GITHUB_TOKEN          - Your GitHub personal access token
ORG_NAME              - GitHub organization name
OUTPUT_DIR            - Output directory for cloned repos (default: "cloned_repos")
OPENAI_API_KEY        - OpenAI API key for AI feedback
MODEL_NAME            - OpenAI model name (e.g., "gpt-4")
MOODLE_URL            - Moodle site URL
MOODLE_TOKEN          - Moodle web service token
```

### ATM Banking System (Main.py)
```
ATM_ASSIGNMENT_REPO_PREFIX    - Repository prefix (e.g., "midterm-exam-atm-")
ATM_MOODLE_COURSE_ID          - Moodle course ID for ATM assignment
ATM_MOODLE_ACTIVITY_ID        - Moodle activity ID for ATM assignment
ATM_MOODLE_GRADE_ITEM_ID      - Moodle grade item ID for ATM assignment
```

### Laravel Event Management (Laravel_grader.py)
```
LARAVEL_ASSIGNMENT_REPO_PREFIX - Repository prefix (e.g., "laravel-event-")
LARAVEL_MOODLE_COURSE_ID       - Moodle course ID for Laravel assignment
LARAVEL_MOODLE_ACTIVITY_ID     - Moodle activity ID for Laravel assignment
LARAVEL_MOODLE_GRADE_ITEM_ID   - Moodle grade item ID for Laravel assignment
```

## Quick Commands

### View Configuration
```bash
python show_config.py
```
Shows all configuration values with sensitive data masked.

### Run Unified Grading System
```bash
python unified_grader.py
```
Interactive menu for both grading systems.

### Run Individual Graders
```bash
python Main.py           # ATM Banking System only
python Laravel_grader.py # Laravel Event Management only
```

## Configuration File Location
`config.py` - Single configuration file for all systems

## How It Works

1. **ATM Banking System (Main.py)**
   - Imports: `ASSIGNMENT_REPO_PREFIX`, `MOODLE_COURSE_ID`, etc.
   - These automatically use the `ATM_*` values from config.py

2. **Laravel Event Management (Laravel_grader.py)**
   - Imports: `LARAVEL_ASSIGNMENT_REPO_PREFIX as ASSIGNMENT_REPO_PREFIX`
   - Uses the `LARAVEL_*` values from config.py

3. **Backward Compatibility**
   - Old scripts using `ASSIGNMENT_REPO_PREFIX` still work
   - They default to ATM values

## Finding Moodle IDs

### Course ID
1. Go to your Moodle course
2. Look at the URL: `moodle.edu/course/view.php?id=3385`
3. The number after `id=` is your course ID

### Activity ID
1. Go to the assignment in Moodle
2. Look at the URL: `moodle.edu/mod/assign/view.php?id=144160`
3. The number after `id=` is your activity ID

### Grade Item ID
1. Method 1: Run `python MoodleIntegration.py` and it will show you the ID
2. Method 2: Go to Gradebook → Setup → Edit grade item, look at URL

## Troubleshooting

**Laravel Moodle IDs set to 0?**
- This is normal for new setup
- Update `LARAVEL_MOODLE_*` values in config.py when ready

**Both graders using same repositories?**
- Check `ATM_ASSIGNMENT_REPO_PREFIX` vs `LARAVEL_ASSIGNMENT_REPO_PREFIX`
- They should be different prefixes

**Main.py not finding repositories?**
- It uses `ATM_ASSIGNMENT_REPO_PREFIX`
- Check if your repo names match this prefix
