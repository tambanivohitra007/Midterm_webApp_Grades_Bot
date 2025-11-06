# Unified Auto-Grading System

## Overview

This unified grading system supports two types of projects:
1. **ATM Banking System (PHP)** - Milestone-based grading with commit-by-commit analysis
2. **Laravel Event Management** - Rubric-based grading with AI feedback

## Features

### ✨ Main Features
- **Dual Grading Systems**: Support for both ATM and Laravel projects
- **Unified Interface**: Single entry point for all grading operations
- **HTML Reports**: Beautiful, detailed HTML reports for both project types
- **JSON Data**: Structured JSON output for programmatic access
- **AI Feedback**: Intelligent analysis and suggestions for Laravel projects
- **Performance Comparison**: Compare student performance across projects

### 📊 Grading Methods

#### ATM Banking System
- **Method**: Milestone-based (23 milestones)
- **Analysis**: Commit-by-commit chronological review
- **Output**: `result.html`, detailed milestone tracking
- **Focus**: Progressive development, version control practices

#### Laravel Event Management
- **Method**: Rubric-based (8 categories)
- **Analysis**: Overall project state assessment
- **Output**: `result.html`, `grading_result.json`
- **Categories**:
  - Models (20 pts) - Relationships, fillables
  - Controllers (20 pts) - Validation, logic
  - Migrations (15 pts) - Schema design, constraints
  - Routes (10 pts) - RESTful routing
  - Views (10 pts) - Blade templates
  - Constraint Logic (15 pts) - Business rules
  - Documentation (10 pts) - README quality
  - Commits (15 pts) - Version control

## Usage

### Quick Start

Run the unified grading system:

```bash
python unified_grader.py
```

### Menu Options

```
1. ATM Banking System (PHP) - Milestone-based grading
2. Laravel Event Management - Rubric-based grading
3. View Grading Reports
4. Compare Student Performance
5. Exit
```

### Running Individual Graders

#### ATM Banking System Only
```bash
python Main.py
```

#### Laravel Projects Only
```bash
python Laravel_grader.py
```

## Configuration

Both graders use the same `config.py` file with **project-specific sections**:

```python
# GitHub Configuration (Shared)
GITHUB_TOKEN = "your_github_token"
ORG_NAME = "your_organization"

# ATM Banking System Configuration
ATM_ASSIGNMENT_REPO_PREFIX = "midterm-exam-atm-"
ATM_MOODLE_COURSE_ID = 3385
ATM_MOODLE_ACTIVITY_ID = 144160
ATM_MOODLE_GRADE_ITEM_ID = 76732

# Laravel Event Management Configuration
LARAVEL_ASSIGNMENT_REPO_PREFIX = "laravel-event-"
LARAVEL_MOODLE_COURSE_ID = 3385
LARAVEL_MOODLE_ACTIVITY_ID = 0  # Update with your activity ID
LARAVEL_MOODLE_GRADE_ITEM_ID = 0  # Update with your grade item ID

# OpenAI Configuration (Shared)
OPENAI_API_KEY = "your_openai_key"
MODEL_NAME = "gpt-4"

# Moodle Configuration (Shared)
MOODLE_URL = "https://lms.apiu.edu"
MOODLE_TOKEN = "your_moodle_token"

# Output (Shared)
OUTPUT_DIR = "cloned_repos"
```

### 🔍 View Your Configuration

To see all configuration values and check for issues:

```bash
python show_config.py
```

This will display:
- ✅ All shared configuration values
- ✅ ATM-specific settings (used by Main.py)
- ✅ Laravel-specific settings (used by Laravel_grader.py)
- ⚠️ Configuration warnings and missing values

## Output Structure

```
cloned_repos/
├── midterm-exam-atm-student1/
│   ├── result.html           # ATM grading report
│   └── [student code]
├── midterm-exam-atm-student2/
│   └── result.html
├── laravel-event-student1/
│   ├── result.html           # Laravel grading report
│   ├── grading_result.json   # Structured data
│   └── [student code]
└── student_summary.txt       # ATM projects summary
```

## Report Features

### ATM Banking System Reports
- 📈 Progressive milestone completion tracking
- 🎯 Detailed per-commit analysis
- ✅ Feature implementation verification
- 📊 Visual progress indicators
- 💬 AI-powered feedback per milestone

### Laravel Event Management Reports
- 🎨 Beautiful gradient header
- 📊 Category-wise scoring with progress bars
- 🤖 AI-powered code review
- 💡 Specific suggestions for improvement
- ⭐ Overall grade (A/B/C/D)

## View Reports

### Option 1: Through Unified Menu
1. Run `python unified_grader.py`
2. Select option 3 (View Grading Reports)
3. Choose project type
4. Select student to view report

### Option 2: Direct Access
Navigate to `cloned_repos/[student-repo]/result.html` and open in browser

### Option 3: JSON Data
For Laravel projects, programmatic access via `grading_result.json`:

```python
import json

with open('cloned_repos/laravel-event-student1/grading_result.json') as f:
    data = json.load(f)
    
print(f"Models Score: {data['Models']['score']}")
print(f"AI Feedback: {data['AI Review']['summary']}")
```

## Performance Comparison

Compare student performance across both project types:

1. Run `python unified_grader.py`
2. Select option 4 (Compare Student Performance)
3. View side-by-side comparison of ATM and Laravel grades

## Troubleshooting

### Common Issues

**Error: Module not found**
```bash
pip install PyGithub gitpython openai
```

**Error: GitHub authentication failed**
- Check your `GITHUB_TOKEN` in `config.py`
- Ensure token has repo access permissions

**Error: OpenAI API error**
- Verify `OPENAI_API_KEY` is valid
- Check API quota/billing

**Error: Repository not found**
- Verify `ORG_NAME` is correct
- Check `ASSIGNMENT_REPO_PREFIX` matches repo names

## Best Practices

### For ATM Projects
- Ensure students make regular commits
- Each milestone should be a separate commit
- README should document features

### For Laravel Projects
- Models should have clear relationships
- Controllers should validate inputs
- Migrations should include constraints
- README should document setup and features

## Dependencies

```
PyGithub>=2.1.1
gitpython>=3.1.40
openai>=1.3.0
```

## License

MIT License - Educational Use

## Support

For issues or questions:
1. Check existing error messages
2. Verify configuration in `config.py`
3. Review student repository structure
4. Check GitHub and OpenAI API status

---

