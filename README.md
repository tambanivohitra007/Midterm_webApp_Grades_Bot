# Student Grades Bot

An automated grading system that clones student repositories from GitHub, evaluates their code using OpenAI's API, and sends personalized grade reports via Microsoft Teams.

## Overview

This project automates the grading workflow for programming assignments by:

1. Cloning student repositories from a GitHub organization
2. Evaluating code quality and functionality using AI-powered analysis
3. Generating detailed grade reports with feedback
4. Sending grades directly to students via Microsoft Teams 1:1 chat

## Project Structure

- `config.py` - Configuration file containing sensitive credentials and settings (DO NOT COMMIT)
- `chatMessage.py` - Microsoft Teams integration for sending grades to students
- `cloned_repos/` - Directory where student repositories are cloned
- `teams_grade_log.txt` - Log file tracking the grading and messaging process

## Features

- **Automated Repository Cloning**: Fetches all student repositories matching a specific prefix from GitHub
- **AI-Powered Grading**: Uses OpenAI's API to evaluate code quality, functionality, and adherence to requirements
- **Bonus/Penalty System**:
  - Awards bonus points for high-quality instruction following (>80% average)
  - Applies late submission penalties based on deadline
- **Microsoft Teams Integration**: Sends personalized grade reports directly to students via Teams chat
- **Comprehensive Logging**: Tracks all operations with detailed logs

## Prerequisites

- Python 3.7+
- GitHub account with access to student repositories
- OpenAI API key
- Microsoft Azure AD application with Teams permissions
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
```

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

### Step 1: Clone and Grade Student Repositories

```bash
python Main.py
```

This script will:
- Clone all student repositories matching the prefix from GitHub
- Evaluate each commit against milestone criteria
- Generate detailed grade reports in `cloned_repos/[repo-name]/result.txt`

### Step 2: Send Grades via Teams

```bash
python chatMessage.py
```

This script will:
- Authenticate you interactively with Microsoft Teams
- Read grade reports from each student's `result.txt`
- Create 1:1 chats with each student
- Send personalized grade messages

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

## Security Notes

- Never commit `config.py` to version control
- Keep all API keys and secrets secure
- Use environment variables for production deployments
- Regularly rotate API keys and client secrets
- Review Azure AD permissions periodically

## Logging

All operations are logged to:
- Console output (stdout)
- `teams_grade_log.txt` file

Log entries include timestamps, severity levels, and detailed operation information.

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

## License

This project is for educational use in academic settings.

## Support

For issues or questions, contact the instructor at the email specified in the configuration.
