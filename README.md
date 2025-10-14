# Student Grades Bot

An automated grading system that clones student repositories from GitHub, evaluates their code using OpenAI's API, and sends personalized grade reports via Microsoft Teams.

## Overview

This project automates the grading workflow for programming assignments by:

1. Cloning student repositories from a GitHub organization
2. Evaluating code quality and functionality using AI-powered analysis
3. Generating detailed grade reports with feedback
4. Sending grades directly to students via Microsoft Teams 1:1 chat

## Expected Student Repository Structure

Students are required to follow this file structure for their ATM Banking System project:

```
atm_project/
│── index.php              # Entry point, redirects to login or dashboard
│── register.php           # User registration form and processing
│── login.php              # User login form + session + failed login handling
│── logout.php             # Destroys session to log out user
│── dashboard.php          # Shows user balance and menu (link to transaction/history)
│── transaction.php        # Combined deposit & withdraw form + processing
│── transfer.php           # User-to-user transfer functionality
│── history.php            # Shows transaction history (filterable)
│── pin_change.php         # PIN change functionality
│
├── includes/
│   ├── db.php             # Database connection via PDO
│   ├── auth.php           # Session/authentication helpers, checks login status
│   ├── helpers.php        # Validation functions, rules, formatting, reusable code
│
├── assets/
│   ├── css/style.css      # Custom styles (Bootstrap optional overrides)
│   └── js/app.js          # JavaScript (UI enhancements, AJAX)
│
├── api/
│   └── process_transaction.php  # AJAX endpoint for transactions
│
├── admin/
│   ├── index.php          # Admin dashboard
│   ├── users.php          # User management
│   └── auth_admin.php     # Admin authentication
│
├── sql/
│   └── schema.sql         # Database schema (users + transactions + activity_log)
│
└── README.md              # Project documentation
```

**Key Requirements:**
- Students must follow this structure for proper grading
- Each milestone corresponds to specific files being created/modified
- The grading system checks for file existence and required code features
- 23 milestones total, covering setup, security, transactions, admin, and code quality

## Milestone Overview

The grading system evaluates 23 milestones across 6 categories (100 points total):

### 1. Basic Setup & Core Features (25 points)
- **Commit 1-7**: Project setup, registration, authentication, dashboard, logout

### 2. Security & Validation (20 points)
- **Commit 8**: Input validation and PIN security
- **Commit 21-22**: CSRF protection implementation

### 3. Transaction Features (25 points)
- **Commit 9**: Dashboard enhancements with recent activities
- **Commit 10**: Deposit & withdraw transactions
- **Commit 11**: Atomic transactions with proper rollback
- **Commit 12**: User-to-user transfers

### 4. Advanced Features (15 points)
- **Commit 13**: Transaction history with filtering and pagination
- **Commit 14**: AJAX refactoring for dynamic updates

### 5. Admin & Logging (10 points)
- **Commit 15**: Admin dashboard with user management
- **Commit 16-17**: Activity logging system

### 6. Additional Security (5 points)
- **Commit 18**: PIN change functionality
- **Commit 19**: Daily withdrawal limits
- **Commit 20**: Transfer rate limiting

### 7. Code Quality (Holistic evaluation)
- **Commit 23**: Documentation, comments, optimization (not separately scored)

**Bonus/Penalties:**
- +5 points: Average quality ≥ 80% (Instruction Following Bonus)
- -5 points: Late submission after deadline

## Grading System Project Structure

- `menu.py` - **Interactive console menu** for managing all grading operations (recommended entry point)
- `Main.py` - Main grading script that clones repositories and evaluates student code
- `MoodleIntegration.py` - Moodle integration for automatic grade uploading to LMS
- `chatMessage.py` - Microsoft Teams integration for sending grades to students
- `verify_mappings.py` - Helper script to verify student email mappings
- `list_students.py` - Helper script to list all student repositories
- `config.py` - Configuration file containing sensitive credentials and settings (DO NOT COMMIT)
- `MOODLE_SETUP.md` - Detailed guide for setting up Moodle Web Services integration
- `cloned_repos/` - Directory where student repositories are cloned
- `teams_grade_log.txt` - Log file tracking the grading and messaging process

## Features

- **Interactive Console Menu**: Simple, user-friendly interface for managing all grading operations
  - Real-time console output with full visibility
  - System status monitoring
  - Confirmation prompts for critical operations
  - No GUI dependencies - works on any terminal
- **Automated Repository Cloning**: Fetches all student repositories matching a specific prefix from GitHub
- **AI-Powered Grading**: Uses OpenAI's API to evaluate code quality, functionality, and adherence to requirements
- **GitHub Username Extraction**: Automatically identifies each student's GitHub username from their commits
- **Email Mapping Verification**: Helper scripts to verify all students are properly mapped to their email addresses
- **Bonus/Penalty System**:
  - Awards bonus points for high-quality instruction following (>80% average)
  - Applies late submission penalties based on deadline
- **Moodle LMS Integration**: Automatically uploads final grades to Moodle via Web Services API
  - Batch grade upload for all students
  - Maps GitHub usernames to Moodle student IDs
  - Detailed success/failure reporting
  - Supports all Moodle assignment types
- **Microsoft Teams Integration**: Sends personalized grade reports directly to students via Teams chat
- **Student Summary Report**: Generates a master summary file with all GitHub usernames and scores
- **Comprehensive Logging**: Tracks all operations with detailed logs

## Prerequisites

- Python 3.7+
- GitHub account with access to student repositories
- OpenAI API key
- Microsoft Azure AD application with Teams permissions (for Teams integration)
- Moodle administrator access (for LMS grade upload)
- Required Python packages:
  - `requests`
  - `msal` (Microsoft Authentication Library)
  - `openai`

## Setup

### 1. Install Dependencies

```bash
pip install requests msal openai
```

### 2. Configure Settings

Create a `config.py` file with the following settings:

```python
# GitHub Configuration
GITHUB_TOKEN = "your_github_token"
ORG_NAME = "your-organization-name"
ASSIGNMENT_REPO_PREFIX = "assignment-prefix-"
OUTPUT_DIR = "cloned_repos"

# OpenAI Configuration
OPENAI_API_KEY = "your_openai_api_key"
MODEL_NAME = "gpt-4"

# Bonus/Penalty Configuration
INSTRUCTION_FOLLOWING_BONUS = 5
INSTRUCTION_THRESHOLD = 80
LATE_SUBMISSION_PENALTY = 5
SUBMISSION_DEADLINE = "2025-10-03 23:59:59"

# Microsoft Teams / Azure AD Configuration
TENANT_ID = "your_tenant_id"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

# Instructor Configuration
INSTRUCTOR_EMAIL = "instructor@university.edu"

# Student Email Mappings
STUDENT_EMAILS = {
    "repo-name": "student@university.edu",
    # Add more mappings here
}

# Moodle Web Services Configuration (optional - for automatic grade upload)
MOODLE_URL = "https://lms.apiu.edu"
MOODLE_TOKEN = "your_web_service_token"
MOODLE_COURSE_ID = 3385
MOODLE_ACTIVITY_ID = 144160  # Assignment module ID
MOODLE_GRADE_ITEM_ID = 76732  # Grade item ID (for API)
```

**Note**: Student email format should be `studentID@university.edu` where the studentID (before @) is used as the Moodle username.

### 3. Azure AD App Registration

1. Register an application in Azure AD
2. Grant the following permissions:
   - `User.Read` (Delegated)
   - `Chat.ReadWrite` (Delegated)
3. Create a client secret
4. Add the credentials to `config.py`

### 4. Add config.py to .gitignore

```bash
echo "config.py" >> .gitignore
```

## Usage

### Interactive Console Menu (Recommended)

Launch the interactive console menu for easy management:

```bash
python menu.py
```

The menu provides a simple interface with the following options:

```
MAIN MENU
────────────────────────────────────────────────────────────────────────────────

  [1] Grade All Students
  [2] Upload Grades to Moodle
  [3] Send Teams Messages
  [4] Verify Email Mappings
  [5] View Student Summary
  [6] View Configuration
  [7] Refresh Status
  [8] Open Config File
  [9] Exit
```

**Features:**
- Real-time console output with full visibility
- System status display (organization, deadline, grading status, students mapped/graded, Moodle configuration)
- Automatic confirmation prompts for critical operations
- Easy access to all grading system functions
- No GUI dependencies - works on any terminal

**Workflow:**
1. **Grade All Students** - Run Main.py to evaluate all repositories
2. **Upload Grades to Moodle** - Automatically upload grades to your LMS
3. **Send Teams Messages** - Notify students with personalized reports
4. **View Student Summary** - Review all grades and statistics

### Manual Script Execution

Alternatively, you can run scripts individually:

#### Step 1: Clone and Grade Student Repositories

```bash
python Main.py
```

This script will:
- Clone all student repositories matching the prefix from GitHub
- Evaluate each commit against milestone criteria
- Generate detailed grade reports in `cloned_repos/[repo-name]/result.txt`

#### Step 2: Send Grades via Teams

```bash
python chatMessage.py
```

This script will:
- Authenticate you interactively with Microsoft Teams
- Read grade reports from each student's `result.txt`
- Create 1:1 chats with each student
- Send personalized grade messages

#### Step 3: Verify Email Mappings

```bash
python verify_mappings.py
```

This script will:
- Check that all repositories are mapped to student emails
- Display verification status for each repository
- Show summary of mapped vs unmapped repositories

## Moodle Integration

The grading system includes automatic grade uploading to Moodle via Web Services API.

### Quick Setup

1. **Enable Moodle Web Services** (requires admin access)
2. **Create a Web Service Token** in Moodle
3. **Find your Course and Assignment IDs** from Moodle URLs
4. **Configure `config.py`** with Moodle credentials
5. **Map student emails** in `STUDENT_EMAILS` (studentID@domain.edu format)
6. **Run the integration** via menu option [2] or `python MoodleIntegration.py`

### Features

- **Batch Grade Upload**: Upload all student grades in one operation
- **Automatic Mapping**: Uses student email prefixes as Moodle usernames
- **Error Handling**: Reports success/failure for each student
- **Results Log**: Saves detailed results to `moodle_update_results.txt`
- **Validation**: Tests connection and permissions before uploading

### Configuration Example

```python
# In config.py
MOODLE_URL = "https://lms.apiu.edu"
MOODLE_TOKEN = "your_web_service_token_here"
MOODLE_COURSE_ID = 3385
MOODLE_ACTIVITY_ID = 144160  # From assignment URL
MOODLE_GRADE_ITEM_ID = 76732  # For API grade updates

# Student emails (ID before @ is used as Moodle username)
STUDENT_EMAILS = {
    "midterm-exam-atm-student1": "202100178@my.apiu.edu",  # Moodle username: 202100178
    "midterm-exam-atm-student2": "202300155@my.apiu.edu",  # Moodle username: 202300155
}
```

### Required Moodle Functions

Your Moodle Web Service must have these functions enabled:
- `core_webservice_get_site_info` - Connection test
- `core_course_get_courses` - Course information
- `core_user_get_users` - Find students
- `core_grades_update_grades` - Update grades
- `gradereport_user_get_grade_items` - Grade items

### Detailed Setup Guide

For complete step-by-step instructions, see **[MOODLE_SETUP.md](MOODLE_SETUP.md)** which covers:
- Enabling Web Services in Moodle
- Creating and configuring web service tokens
- Finding Course and Assignment IDs
- Troubleshooting common issues
- Security best practices

### Usage from Menu

```bash
python menu.py
# Select option [2] Upload Grades to Moodle
```

The script will:
1. Load student data from `config.py`
2. Read grades from `student_summary.txt`
3. Test Moodle connection
4. Ask for confirmation
5. Upload all grades in batch
6. Save results to `cloned_repos/moodle_update_results.txt`

### Manual Execution

```bash
python MoodleIntegration.py
```

This will run the full test suite and allow you to upload grades directly.

## Ensuring Consistent Grading

To ensure student scores don't change when running the grading script multiple times, use one of these approaches:

### Method 1: Freeze Grading (Recommended for Final Grades)

After the first grading run, edit `config.py`:

```python
FREEZE_GRADING = True  # Locks scores, prevents pulling new commits
```

**When to use:**
- After the deadline has passed
- When finalizing grades before sending to students
- To ensure consistency when re-running the script

### Method 2: Grade Up to Deadline

Set a cutoff date in `config.py`:

```python
GRADE_COMMITS_UNTIL = "2025-10-03 23:59:59"  # Only grade commits before this date
```

**When to use:**
- To only grade commits before the deadline
- To ignore late commits
- When students continue working after the deadline

### Method 3: Combination (Most Reliable)

Use both settings for maximum consistency:

```python
FREEZE_GRADING = True
GRADE_COMMITS_UNTIL = "2025-10-03 23:59:59"
```

This ensures:
1. Only commits before the deadline are graded
2. No new commits are pulled from GitHub
3. Scores remain identical across multiple runs

## Configuration Details

### GitHub Settings

- `GITHUB_TOKEN`: Personal access token with repo read permissions
- `ORG_NAME`: GitHub organization containing student repositories
- `ASSIGNMENT_REPO_PREFIX`: Prefix used to identify assignment repositories

### OpenAI Settings

- `OPENAI_API_KEY`: API key for OpenAI services
- `MODEL_NAME`: Model to use for grading (e.g., "gpt-4")

### Grading Rules

- `INSTRUCTION_FOLLOWING_BONUS`: Points awarded for excellent instruction following
- `INSTRUCTION_THRESHOLD`: Minimum quality percentage to earn bonus
- `LATE_SUBMISSION_PENALTY`: Points deducted for late submissions
- `SUBMISSION_DEADLINE`: Deadline for submissions (format: YYYY-MM-DD HH:MM:SS)

### Grading Consistency

These settings ensure scores remain consistent across multiple grading runs:

- `FREEZE_GRADING`: Set to `True` to prevent pulling new commits (keeps scores locked)
  - When `False`: Always grades the latest commits (scores may change)
  - When `True`: Uses existing repository state (scores remain consistent)
- `GRADE_COMMITS_UNTIL`: Grade only commits before this date (format: YYYY-MM-DD HH:MM:SS)
  - Leave as empty string `""` to grade all commits
  - Set to deadline date to only grade commits before deadline

### Microsoft Teams

- `TENANT_ID`: Azure AD tenant identifier
- `CLIENT_ID`: Application (client) ID from Azure AD
- `CLIENT_SECRET`: Client secret from Azure AD
- `INSTRUCTOR_EMAIL`: Email address of the instructor
- `STUDENT_EMAILS`: Dictionary mapping repository names to student email addresses

### Moodle Integration

- `MOODLE_URL`: Your Moodle site URL (e.g., https://lms.apiu.edu)
- `MOODLE_TOKEN`: Web service token from Moodle admin panel
- `MOODLE_COURSE_ID`: Course ID (from course URL)
- `MOODLE_ACTIVITY_ID`: Assignment module ID (from mod/assign/view.php?id=XXXXX)
- `MOODLE_GRADE_ITEM_ID`: Grade item ID for API updates (found via MoodleIntegration.py)
- **Note**: The email prefix in `STUDENT_EMAILS` (before @) is used as the Moodle username

## Security Notes

- Never commit `config.py` to version control
- Keep all API keys and secrets secure
- Use environment variables for production deployments
- Regularly rotate API keys, client secrets, and web service tokens
- Review Azure AD permissions periodically
- Secure Moodle web service tokens like passwords
- Use dedicated service accounts with minimal permissions
- Enable Moodle web service IP restrictions if possible

## Logging

All operations are logged to:
- Console output (stdout)
- `teams_grade_log.txt` file

Log entries include timestamps, severity levels, and detailed operation information.

## Output Files

After running the grading system, you'll find the following outputs:

### HTML Grade Reports (New!)
- **Location**: `cloned_repos/[repo-name]/result.html`
- **Content**: Responsive HTML version of grade reports
- **Features**:
  - Mobile-friendly design
  - Color-coded milestone scores
  - Organized by commit/milestone
  - Easy to share via web or email

### Individual Grade Reports
- **Location**: `cloned_repos/[repo-name]/result.txt`
- **Content**: Detailed feedback for each milestone with scores and suggestions
- **Includes**: GitHub username, repository info, milestone-by-milestone analysis

### Student Summary
- **Location**: `cloned_repos/student_summary.txt`
- **Content**: Master list of all students with their:
  - Repository name
  - GitHub username
  - Final score (out of 100)
  - Letter grade

**Example**:
```
================================================================================
STUDENT GRADING SUMMARY
Generated: 2025-10-13 14:30:00
================================================================================

Repository: midterm-exam-atm-student1
GitHub Username: @student1-github
Final Score: 85.50/100
Grade: A (Excellent)
--------------------------------------------------------------------------------

Repository: midterm-exam-atm-student2
GitHub Username: @student2-github
Final Score: 72.30/100
Grade: B (Good)
--------------------------------------------------------------------------------
```

### Moodle Upload Results
- **Location**: `cloned_repos/moodle_update_results.txt`
- **Content**: Results from Moodle grade upload
- **Includes**:
  - Total students processed
  - Success/failure counts
  - Detailed status for each student
  - Moodle username mapping

This summary file is useful for:
- Quick overview of all student scores
- Mapping GitHub usernames to repositories
- Grade book imports
- Class statistics
- Moodle grade upload preparation

## GitHub Username Extraction

The system automatically extracts each student's GitHub username using two methods:

### Method 1: GitHub API (Primary)
- Queries repository contributors via GitHub API
- Identifies the contributor with the most commits
- Most reliable method

### Method 2: Commit Analysis (Fallback)
- Analyzes commit author emails
- Extracts username from GitHub noreply emails
- Format: `username@users.noreply.github.com` or `ID+username@users.noreply.github.com`

### Usage

The GitHub username is automatically:
1. Displayed in the console during grading
2. Included in each student's grade report
3. Listed in the master student summary file

You can optionally map GitHub usernames to student emails in `config.py`:

```python
GITHUB_USERNAME_TO_EMAIL = {
    "student-github-username": "student@university.edu",
}
```

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:
1. Ensure your Azure AD app has the correct permissions
2. Verify that permissions have been granted admin consent
3. Check that the client secret hasn't expired

### API Rate Limiting

- The script includes a 1-second delay between messages to avoid throttling
- If you hit rate limits, increase the delay in `chatMessage.py`

### Missing Grade Files

If students are skipped:
- Verify that `result.txt` exists in their repository directory
- Check file encoding (should be UTF-8)
- Review logs for specific error messages

### Moodle Integration Issues

If Moodle grade upload fails:
- Verify web services are enabled in Moodle admin panel
- Check that your token has `core_grades_update_grades` permission
- Ensure student usernames match Moodle (use email prefix)
- Review `moodle_update_results.txt` for specific errors
- Test connection with `python MoodleIntegration.py`
- See [MOODLE_SETUP.md](MOODLE_SETUP.md) for detailed troubleshooting

## License

This project is for educational use in academic settings.

## Support

For issues or questions, contact the instructor at the email specified in the configuration.
