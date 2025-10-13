import os
from github import Github
from git import Repo, GitCommandError, NULL_TREE
import json
from openai import OpenAI
from datetime import datetime

# ------------------------------
# CONFIGURATION - Import from config.py
# ------------------------------
try:
    from config import (
        GITHUB_TOKEN,
        ORG_NAME,
        ASSIGNMENT_REPO_PREFIX,
        OUTPUT_DIR,
        OPENAI_API_KEY,
        MODEL_NAME,
        INSTRUCTION_FOLLOWING_BONUS,
        INSTRUCTION_THRESHOLD,
        LATE_SUBMISSION_PENALTY,
        SUBMISSION_DEADLINE,
        FREEZE_GRADING,
        GRADE_COMMITS_UNTIL
    )
except ImportError:
    print("❌ Error: config.py not found!")
    print("Please copy config.example.py to config.py and fill in your credentials.")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# ------------------------------
# MILESTONE GUIDE WITH WEIGHTED SCORES (Total = 100 points)
# ------------------------------
MILESTONES = {
    # Basic Setup & Core Features (25 points)
    1: {
        "desc": "Initial project setup with file structure",
        "files": ["all folders created"],
        "weight": 2,
        "criteria": [
            "Proper folder structure (includes/, assets/, sql/, admin/)",
            "Basic files created",
            "Clear organization"
        ]
    },
    2: {
        "desc": "Added registration form",
        "files": ["register.php"],
        "weight": 3,
        "criteria": [
            "HTML form with required fields (name, email, PIN)",
            "Form structure is valid",
            "Basic styling or layout"
        ]
    },
    3: {
        "desc": "Created database schema and users table",
        "files": ["sql/schema.sql"],
        "weight": 4,
        "criteria": [
            "Users table with proper columns (id, name, email, pin, balance)",
            "Appropriate data types",
            "Primary key defined",
            "Default balance set"
        ]
    },
    4: {
        "desc": "User registration saved into DB",
        "files": ["register.php", "includes/db.php"],
        "weight": 4,
        "criteria": [
            "Database connection established",
            "INSERT query to save user",
            "PIN is hashed (password_hash or similar)",
            "Basic error handling"
        ]
    },
    5: {
        "desc": "Login with session and failed login handling",
        "files": ["login.php", "includes/auth.php"],
        "weight": 6,
        "criteria": [
            "Login form with email and PIN",
            "PIN verification (password_verify or similar)",
            "Session started and user ID stored",
            "Failed login message displayed",
            "Redirect to dashboard on success"
        ]
    },
    6: {
        "desc": "Created dashboard page with balance",
        "files": ["dashboard.php"],
        "weight": 4,
        "criteria": [
            "Session check to protect page",
            "User data fetched from database",
            "Balance displayed",
            "Basic navigation or menu"
        ]
    },
    7: {
        "desc": "Added logout functionality",
        "files": ["logout.php"],
        "weight": 2,
        "criteria": [
            "Session destroyed (session_destroy)",
            "User redirected to login page",
            "Works correctly"
        ]
    },

    # Security & Validation (20 points)
    8: {
        "desc": "Added validation and PIN security",
        "files": ["helpers.php", "register.php", "login.php"],
        "weight": 8,
        "criteria": [
            "Input validation functions created",
            "Email format validation",
            "PIN length/format requirements enforced",
            "Sanitization of inputs (htmlspecialchars, etc.)",
            "Validation applied in register and login"
        ]
    },
    21: {
        "desc": "Add CSRF token helper functions",
        "files": ["includes/helpers.php", "includes/auth.php"],
        "weight": 5,
        "criteria": [
            "generate_csrf_token() function creates unique token",
            "Token stored in $_SESSION",
            "validate_csrf_token($token) function verifies token",
            "csrf_token_field() returns hidden input HTML",
            "Proper implementation using random_bytes() or similar",
            "Token generated on login/session start"
        ]
    },
    22: {
        "desc": "Integrate CSRF protection across all forms",
        "files": ["register.php", "login.php", "transaction.php", "transfer.php", "pin_change.php", "admin/*.php"],
        "weight": 7,
        "criteria": [
            "CSRF tokens added to ALL state-changing forms",
            "Hidden input fields with CSRF token in each form",
            "Token validation performed before processing each form",
            "Registration, Login, Transactions, Transfers protected",
            "Admin forms and PIN change protected",
            "Proper error messages for invalid/missing tokens",
            "Prevents Cross-Site Request Forgery attacks"
        ]
    },

    # Transaction Features (25 points)
    9: {
        "desc": "Dashboard enhancements with recent activities",
        "files": ["dashboard.php"],
        "weight": 3,
        "criteria": [
            "Recent transactions displayed (5 most recent)",
            "Query to fetch recent activities from transactions table",
            "Formatted display (table or list)",
            "Shows transaction type, amount, and timestamp",
            "Activities properly logged for display"
        ]
    },
    10: {
        "desc": "Added combined transaction page (deposit & withdraw)",
        "files": ["transaction.php", "helpers.php", "auth.php"],
        "weight": 8,
        "criteria": [
            "Form with deposit and withdraw options",
            "Amount validation (positive, numeric)",
            "Balance updated in database (UPDATE query)",
            "Insufficient funds check for withdrawal",
            "Transaction recorded in transactions table",
            "Success/error messages shown"
        ]
    },
    11: {
        "desc": "Atomic Transactions & Enhanced Logging",
        "files": ["transaction.php", "sql/schema.sql"],
        "weight": 8,
        "criteria": [
            "Transactions table created in schema",
            "BEGIN TRANSACTION used",
            "COMMIT on success, ROLLBACK on failure",
            "Transaction log includes user_id, type, amount, timestamp",
            "Proper error handling"
        ]
    },
    12: {
        "desc": "Implement User-to-User Transfers",
        "files": ["transfer.php", "transaction.php", "helpers.php"],
        "weight": 6,
        "criteria": [
            "Transfer form with recipient selection/input",
            "Sender balance decreased",
            "Recipient balance increased",
            "Both updates in single transaction (atomic)",
            "Validation: sufficient funds, valid recipient",
            "Both transactions logged"
        ]
    },

    # Advanced Features (15 points)
    13: {
        "desc": "Advanced Transaction History with Filtering & Pagination",
        "files": ["history.php", "helpers.php"],
        "weight": 7,
        "criteria": [
            "Transaction history page created",
            "Filter by type (deposit/withdraw/transfer)",
            "Filter by date range",
            "Pagination implemented (LIMIT, OFFSET)",
            "Navigation between pages works"
        ]
    },
    14: {
        "desc": "Refactor Transactions with AJAX",
        "files": ["dashboard.php", "assets/js/app.js", "api/process_transaction.php"],
        "weight": 8,
        "criteria": [
            "JavaScript AJAX code written",
            "API endpoint created (process_transaction.php)",
            "JSON response from API",
            "Page updates without refresh",
            "Error handling in JavaScript"
        ]
    },

    # Admin & Logging (10 points)
    15: {
        "desc": "Develop Admin Dashboard with User Management",
        "files": ["admin/index.php", "admin/users.php", "admin/auth_admin.php", "includes/auth.php"],
        "weight": 5,
        "criteria": [
            "Admin authentication mechanism",
            "Admin dashboard page",
            "List all users",
            "Admin can view user details",
            "Basic admin role check"
        ]
    },
    16: {
        "desc": "Add activity logging schema and helper",
        "files": ["sql/schema.sql", "includes/helpers.php"],
        "weight": 2,
        "criteria": [
            "Activity_log table created with proper structure",
            "Columns: id, user_id, activity_type, details, ip_address, created_at",
            "Foreign key relationship to users table",
            "Helper function log_activity() to record events",
            "Function captures user_id, action, IP address"
        ]
    },
    17: {
        "desc": "Integrate activity logging for core actions",
        "files": ["login.php", "logout.php"],
        "weight": 3,
        "criteria": [
            "Login action logged",
            "Logout action logged",
            "IP address captured",
            "Timestamp recorded"
        ]
    },

    # Additional Security Features (5 points)
    18: {
        "desc": "Implement PIN change functionality",
        "files": ["pin_change.php", "dashboard.php", "includes/helpers.php"],
        "weight": 2,
        "criteria": [
            "PIN change form created",
            "Old PIN verified",
            "New PIN hashed",
            "Database updated",
            "Link from dashboard"
        ]
    },
    19: {
        "desc": "Enforce daily withdrawal limits",
        "files": ["transaction.php", "includes/helpers.php"],
        "weight": 2,
        "criteria": [
            "Function to check daily withdrawal total (last 24 hours)",
            "Realistic daily limit enforced (e.g., $5,000/day)",
            "Query sums all withdrawals within last 24 hours",
            "Rejection if current withdrawal + 24hr sum > limit",
            "Clear error message when limit exceeded"
        ]
    },
    20: {
        "desc": "Implement rate limiting on transfers",
        "files": ["transfer.php", "api/process_transaction.php"],
        "weight": 1,
        "criteria": [
            "Track transfer attempts in activity_log or transactions table",
            "Limit enforced (e.g., max 10 transfers per hour)",
            "Count recent transfers before processing",
            "Error message displayed when rate limit exceeded",
            "Prevents spam/abuse of transfer feature"
        ]
    },

    # Code Quality (evaluated holistically, not separately scored)
    23: {
        "desc": "Code Quality & Documentation",
        "files": ["includes/helpers.php", "includes/auth.php", "all PHP files"],
        "weight": 0,
        "criteria": [
            "Comprehensive PHPDoc comments for all functions",
            "Parameters, return values, and purpose documented",
            "Inline comments explain complex logic",
            "Functions have clear, descriptive names",
            "Proper indentation and code formatting",
            "Optimized database queries (prepared statements)",
            "Duplicate code refactored into reusable functions",
            "No major security vulnerabilities",
            "Business rules and assumptions documented"
        ]
    }
}

# ------------------------------
# HELPER FUNCTION TO GET STUDENT GITHUB USERNAME
# ------------------------------
def get_student_github_username(repo, commit_list):
    """
    Extract the student's GitHub username from the repository.
    Uses commits to find the primary contributor (student).
    """
    try:
        # Method 1: Get contributors from GitHub API (most reliable)
        try:
            contributors = repo.get_contributors()
            # Filter contributors and get the one with most contributions
            # Typically the student will have the most commits
            contributor_list = [(c.login, c.contributions) for c in contributors]
            if contributor_list:
                # Sort by contributions (descending) and get the top one
                contributor_list.sort(key=lambda x: x[1], reverse=True)
                return contributor_list[0][0]  # Return username with most contributions
        except Exception as e:
            print(f"   ⚠️ Could not get contributors via API: {e}")

        # Method 2: Extract from commit authors (fallback)
        if commit_list:
            # Count commits per author email
            author_emails = {}
            for commit in commit_list:
                email = commit.author.email
                author_emails[email] = author_emails.get(email, 0) + 1

            # Get the author with most commits
            if author_emails:
                most_active_email = max(author_emails, key=author_emails.get)
                # Extract username from email (if it's a GitHub noreply email)
                if '@users.noreply.github.com' in most_active_email:
                    # Format: username@users.noreply.github.com or ID+username@users.noreply.github.com
                    username_part = most_active_email.split('@')[0]
                    if '+' in username_part:
                        return username_part.split('+')[1]
                    else:
                        return username_part
                else:
                    # Return the email as identifier
                    return most_active_email.split('@')[0]

        return "unknown"
    except Exception as e:
        print(f"   ⚠️ Error extracting GitHub username: {e}")
        return "unknown"


# ------------------------------
# TESTING HELPER FUNCTIONS
# ------------------------------
def check_files_exist(repo_path, expected_files):
    """Check if expected files exist in the repository"""
    found_files = []
    missing_files = []

    for file_pattern in expected_files:
        if file_pattern == "all folders created":
            # Check for common folder structure
            folders = ["includes", "assets", "sql", "admin"]
            existing = [f for f in folders if os.path.exists(os.path.join(repo_path, f))]
            if len(existing) >= 2:
                found_files.append(f"{len(existing)} folders found")
            else:
                missing_files.append("folder structure incomplete")
        elif "*" in file_pattern or "admin/*.php" in file_pattern:
            # Pattern matching
            import glob
            matches = glob.glob(os.path.join(repo_path, file_pattern.replace("/", os.sep)))
            if matches:
                found_files.append(file_pattern)
            else:
                missing_files.append(file_pattern)
        else:
            # Direct file check
            file_path = os.path.join(repo_path, file_pattern.replace("/", os.sep))
            if os.path.exists(file_path):
                found_files.append(file_pattern)
            else:
                missing_files.append(file_pattern)

    return found_files, missing_files


def check_code_features(repo_path, milestone):
    """Check if specific code features are present in the files - FLEXIBLE for junior developers"""
    milestone_num = None
    for num, ms in MILESTONES.items():
        if ms == milestone:
            milestone_num = num
            break

    if not milestone_num:
        return []

    features_found = []

    # Define what to look for based on milestone - WITH ALTERNATIVES for junior devs
    # Each keyword can have multiple variations
    checks = {
        1: {"folders": ["includes", "assets", "sql", "css", "js", "images"]},  # Accept any relevant folders
        2: {"files": ["register.php", "signup.php"], "keywords": [["form", "<form"], ["input", "text", "email"]]},
        3: {"files": ["sql/schema.sql", "schema.sql", "database.sql", "db.sql"], "keywords": [["CREATE TABLE", "CREATE"], ["users", "user"]]},
        4: {"files": ["register.php", "signup.php"], "keywords": [["INSERT", "insert into"], ["password_hash", "hash", "md5", "sha"]]},
        5: {"files": ["login.php", "signin.php"], "keywords": [["session_start", "session"], ["password_verify", "verify", "=="], ["$_SESSION", "session"]]},
        6: {"files": ["dashboard.php", "home.php", "index.php"], "keywords": [["SELECT", "select"], ["balance", "amount"], ["$_SESSION", "session"]]},
        7: {"files": ["logout.php", "signout.php"], "keywords": [["session_destroy", "session_unset", "unset", "destroy"]]},
        8: {"files": ["helpers.php", "register.php", "functions.php", "validation.php"], "keywords": [["validate", "check", "verify"], ["filter", "sanitize", "clean"], ["htmlspecialchars", "strip_tags", "escape"]]},
        9: {"files": ["dashboard.php", "home.php"], "keywords": [["transaction", "history"], ["ORDER BY", "order"], ["LIMIT", "limit"]]},
        10: {"files": ["transaction.php", "transactions.php"], "keywords": [["deposit", "withdraw"], ["UPDATE", "update"], ["balance", "amount"]]},
        11: {"files": ["transaction.php", "transactions.php"], "keywords": [["BEGIN", "START TRANSACTION", "begin"], ["COMMIT", "commit"], ["ROLLBACK", "rollback"]]},
        12: {"files": ["transfer.php", "send.php"], "keywords": [["transfer", "send"], ["UPDATE", "update"], ["balance", "amount"]]},
        13: {"files": ["history.php", "transactions.php"], "keywords": [["WHERE", "where"], ["LIMIT", "limit"], ["OFFSET", "offset", "page"]]},
        14: {"files": ["app.js", "main.js", "script.js", "process_transaction.php", "api"], "keywords": [["fetch", "XMLHttpRequest", "ajax", "$.ajax"], ["json_encode", "json"]]},
        15: {"files": ["admin/index.php", "admin/users.php", "admin/dashboard.php", "admin"], "keywords": [["admin", "role"], ["SELECT", "select"], ["users", "user"]]},
        16: {"files": ["schema.sql", "helpers.php", "functions.php"], "keywords": [["activity_log", "log", "audit"], ["CREATE TABLE", "CREATE"]]},
        17: {"files": ["login.php", "logout.php"], "keywords": [["log_activity", "log", "insert"], ["INSERT", "insert"]]},
        18: {"files": ["pin_change.php", "change_pin.php", "update_pin.php"], "keywords": [["password_hash", "hash", "md5"], ["UPDATE", "update"], ["pin", "password"]]},
        19: {"files": ["transaction.php", "withdraw.php"], "keywords": [["SUM", "sum", "total"], ["daily", "day", "date"], ["limit", "max"]]},
        20: {"files": ["transfer.php", "send.php"], "keywords": [["rate", "limit", "count"], ["time", "timestamp", "date"]]},
        21: {"files": ["helpers.php", "functions.php", "csrf.php"], "keywords": [["csrf", "token"], ["random_bytes", "rand", "uniqid"]]},
        22: {"files": ["register.php", "login.php", "transaction.php", "transfer.php"], "keywords": [["csrf", "token"], ["hidden", "input"]]},
    }

    if milestone_num not in checks:
        return []

    check_config = checks[milestone_num]

    # Check files with more flexibility
    if "files" in check_config:
        for file_name in check_config["files"]:
            file_path = os.path.join(repo_path, file_name.replace("/", os.sep))
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()

                    # Check for keywords with alternatives
                    if "keywords" in check_config:
                        found_count = 0
                        for keyword_group in check_config["keywords"]:
                            # If keyword_group is a list, check if ANY variant exists
                            if isinstance(keyword_group, list):
                                if any(kw.lower() in content for kw in keyword_group):
                                    found_count += 1
                            # If single keyword
                            elif keyword_group.lower() in content:
                                found_count += 1

                        if found_count > 0:
                            percentage = (found_count / len(check_config['keywords'])) * 100
                            features_found.append(f"{file_name}: {found_count}/{len(check_config['keywords'])} features ({percentage:.0f}%)")
                except Exception:
                    pass

    # Check folders - be flexible, accept any reasonable folder
    if "folders" in check_config:
        existing_folders = [f for f in check_config["folders"] if os.path.exists(os.path.join(repo_path, f))]
        if existing_folders:
            features_found.append(f"Project structure: {len(existing_folders)} folders created")

    return features_found


def test_based_grading(repo_path, commit_message, milestone):
    """Grade milestone based on file existence and feature checking - GENEROUS for junior developers"""
    milestone_weight = milestone.get('weight', 0)

    if milestone_weight == 0:
        return {"quality_score": 100, "remark": "Code quality milestone - not separately graded"}

    # Check if files exist
    found_files, missing_files = check_files_exist(repo_path, milestone.get('files', []))

    # Check for code features
    features_found = check_code_features(repo_path, milestone)

    # Calculate score based on findings - BE GENEROUS
    score = 0
    remarks = []

    # File existence: More generous scoring (30% of total)
    if found_files:
        if not missing_files:
            score += 30
            remarks.append(f"✓ Files created")
        else:
            file_percentage = len(found_files) / (len(found_files) + len(missing_files))
            score += int(30 * file_percentage)
            remarks.append(f"✓ {len(found_files)} file(s) found")

    # Feature checking: Very generous (70% of score)
    if features_found:
        # Parse feature percentages from features_found
        total_feature_percentage = 0
        feature_count = 0

        for feature in features_found:
            # Extract percentage if present
            if "%" in feature:
                try:
                    pct = int(feature.split("(")[1].split("%")[0])
                    total_feature_percentage += pct
                    feature_count += 1
                except:
                    # If can't parse, assume 80% (be generous)
                    total_feature_percentage += 80
                    feature_count += 1
            else:
                # No percentage means folders or structure - give 90%
                total_feature_percentage += 90
                feature_count += 1

        if feature_count > 0:
            avg_feature_percentage = total_feature_percentage / feature_count
            # Convert to score (70% max) and be generous
            feature_score = int((avg_feature_percentage / 100) * 70)
            score += feature_score
            remarks.append(f"✓ Implementation: {avg_feature_percentage:.0f}%")
    else:
        # Even if no features detected, give some credit if files exist
        if found_files:
            score += 35  # Give 35% for having files even without detected features
            remarks.append("Basic setup present")

    # Generous bonuses
    # Bonus for commit message relevance
    milestone_keywords = milestone['desc'].lower().split()[:3]
    if any(kw in commit_message.lower() for kw in milestone_keywords):
        score = min(score + 5, 100)

    # MINIMUM SCORES (very generous for junior developers)
    if found_files and features_found:
        score = max(score, 70)  # If files + features exist, minimum 70%
    elif found_files:
        score = max(score, 55)  # If just files exist, minimum 55%
    elif features_found:
        score = max(score, 60)  # If features detected, minimum 60%

    # Cap at 100
    score = min(score, 100)

    return {
        "quality_score": score,
        "remark": "; ".join(remarks) if remarks else "Milestone attempted"
    }


# ------------------------------
def analyze_commit_with_ai(commit_message, diff_text, milestone, repo_path=None):
    """Send commit + diff + milestone to AI and get a quality percentage (0-100) for this milestone"""

    milestone_weight = milestone.get('weight', 0)
    # Build criteria list for the prompt
    criteria_text = "\n".join([f"  - {c}" for c in milestone.get('criteria', [])])

    prompt = f"""
You are a fair, flexible, and supportive grader for a Banking System project milestone.

MILESTONE: {milestone['desc']}
MILESTONE WEIGHT: {milestone_weight} points (out of 100 total for all milestones)
EXPECTED FILES: {', '.join(milestone['files']) if milestone.get('files') else 'N/A'}

GRADING CRITERIA (check each point):
{criteria_text if criteria_text else "  - General implementation quality"}

STUDENT COMMIT MESSAGE:
{commit_message}

CODE CHANGES (diff):
{diff_text[:4000]}

GRADING PHILOSOPHY:
You are evaluating student work, not professional production code. Be FLEXIBLE and GENEROUS while being fair.
- Students are learning, so give credit for honest attempts and functional implementations
- Focus on whether the core functionality works, not perfection
- Don't penalize heavily for missing advanced features or edge cases
- If the basic requirement is met, start at 70% and adjust up or down

EVALUATION STEPS:
1. Did the student make relevant file changes matching this milestone?
2. Is the basic functionality present (even if not perfect)?
3. Does it show understanding of the concept?
4. Be LENIENT on minor issues, styling, or missing edge cases

REVISED QUALITY SCORE GUIDELINES (be flexible and generous):
- 90-100%: Excellent implementation, all/most criteria met, works well
- 75-89%: Good implementation, core functionality works, minor issues are acceptable
- 60-74%: Basic implementation present, shows understanding, may have some issues
- 45-59%: Partial implementation, shows effort but incomplete or has problems
- 25-44%: Minimal implementation, shows some attempt but lacking key parts
- 0-24%: Not implemented, no relevant changes, or completely wrong

IMPORTANT GRADING RULES:
1. If relevant files are modified and basic functionality exists → START AT 70%
2. If student attempted the milestone but incomplete → give 50-65%
3. If code shows understanding but has bugs → give 60-75%
4. Only give below 50% if milestone barely attempted or wrong approach
5. Give 80-90% if it works reasonably well (perfection not required)
6. Reserve 0-40% for truly missing/wrong implementations

BE GENEROUS: Students are learning. Credit effort and functional code appropriately.

Respond ONLY in JSON format:
{{
  "quality_score": <0-100>,
  "remark": "<brief positive or constructive comment>"
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content.strip()
        # Extract JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != -1:
            raw_json = raw[start:end]
        else:
            raw_json = raw
        result = json.loads(raw_json)

        # Handle both old "score" and new "quality_score" keys for compatibility
        if "quality_score" not in result and "score" in result:
            result["quality_score"] = result["score"]

        return result
    except Exception as e:
        return {"quality_score": 0, "remark": f"⚠️ AI error: {e}"}


# ------------------------------
# GITHUB CLONING AND GRADING
# ------------------------------
print("="*70)
print("🎓 STUDENT GRADING SYSTEM")
print("="*70)
print(f"Organization: {ORG_NAME}")
print(f"Assignment Prefix: {ASSIGNMENT_REPO_PREFIX}")
print(f"Submission Deadline: {SUBMISSION_DEADLINE}")

# Display grading configuration
if FREEZE_GRADING:
    print("\n🔒 FREEZE_GRADING: ENABLED")
    print("   → Scores are locked and will remain consistent across runs")
    print("   → Repositories will NOT be updated with new commits")
else:
    print("\n🔓 FREEZE_GRADING: DISABLED")
    print("   → Repositories will be updated with latest commits")
    print("   → Scores may change if students make new commits")

if GRADE_COMMITS_UNTIL:
    print(f"\n📅 GRADE_COMMITS_UNTIL: {GRADE_COMMITS_UNTIL}")
    print(f"   → Only commits before this date will be graded")
else:
    print("\n📅 GRADE_COMMITS_UNTIL: Not set")
    print("   → All commits will be graded")

print("="*70 + "\n")

g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)
repos = [repo for repo in org.get_repos() if repo.name.startswith(ASSIGNMENT_REPO_PREFIX)]
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prepare to collect student information
student_summary = []

for repo in repos:
    print(f"\n📦 Processing {repo.full_name} ...")
    local_path = os.path.join(OUTPUT_DIR, repo.name)
    result_file = os.path.join(local_path, "result.txt")

    try:
        if not os.path.exists(local_path):
            print("🔄 Cloning repository...")
            Repo.clone_from(
                repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@"),
                local_path
            )
        else:
            if FREEZE_GRADING:
                print("🔒 FREEZE_GRADING enabled - Using existing repository state (no pull)")
                print("   Scores will remain consistent across multiple runs")
            else:
                print("🔄 Repo already exists. Pulling latest changes...")
                r = Repo(local_path)
                r.remotes.origin.pull()

        # Iterate commits
        r = Repo(local_path)
        commit_list = list(r.iter_commits())
        commit_list.reverse()  # chronological order

        # Extract student's GitHub username
        student_github_username = get_student_github_username(repo, commit_list)
        print(f"👤 Student GitHub Username: {student_github_username}")

        # Filter commits by deadline if GRADE_COMMITS_UNTIL is set
        if GRADE_COMMITS_UNTIL:
            try:
                cutoff_date = datetime.strptime(GRADE_COMMITS_UNTIL, "%Y-%m-%d %H:%M:%S")
                original_count = len(commit_list)
                commit_list = [c for c in commit_list if datetime.fromtimestamp(c.committed_date) <= cutoff_date]
                filtered_count = len(commit_list)
                if filtered_count < original_count:
                    print(f"📅 Filtering commits: Grading only {filtered_count}/{original_count} commits before {GRADE_COMMITS_UNTIL}")
            except Exception as e:
                print(f"⚠️ Warning: Could not parse GRADE_COMMITS_UNTIL: {e}")

        student_scores = []
        total_weighted_score = 0.0
        total_possible_weight = 0

        # Prepare output log for file - Teams-friendly markdown format
        output_log = []
        output_log.append(f"# 📊 DETAILED GRADING REPORT\n")
        output_log.append(f"**Student Repository:** {repo.name}")
        output_log.append(f"**GitHub Username:** @{student_github_username}")
        output_log.append(f"**Repository Path:** {repo.full_name}")
        output_log.append(f"**Graded on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_log.append(f"**Submission Deadline:** {SUBMISSION_DEADLINE}")

        # Add grading freeze notice if enabled
        if FREEZE_GRADING:
            output_log.append(f"\n⚠️ **GRADING LOCKED:** Scores are frozen and will not change with new commits.")
        if GRADE_COMMITS_UNTIL:
            output_log.append(f"\n📅 **Grading Cutoff:** Only commits before {GRADE_COMMITS_UNTIL} are graded.")

        output_log.append("\n---\n")
        output_log.append("This report provides detailed feedback on each milestone of your project.")
        output_log.append("Please review the criteria, your implementation, and suggestions for improvement.\n")

        for i, commit in enumerate(commit_list, start=1):
            milestone = MILESTONES.get(i)
            if not milestone:
                continue  # skip extra commits beyond milestones

            # Diff
            if commit.parents:
                diffs = commit.diff(commit.parents[0], create_patch=True)
            else:
                diffs = commit.diff(NULL_TREE, create_patch=True)

            diff_text = ""
            for diff in diffs:
                try:
                    diff_text += diff.diff.decode("utf-8", errors="ignore") + "\n"
                except Exception as e:
                    diff_text += f"⚠️ Could not decode diff: {e}\n"

            # Check if diff is empty or too small (likely no real changes)
            if len(diff_text.strip()) < 10:
                milestone_weight = milestone.get('weight', 0)

                # Print to console
                print(f"\n{'='*70}")
                print(f"Milestone {i}: {milestone['desc']}")
                print(f"{'='*70}")
                print(f"Commit message: {commit.message.strip()}")
                print(f"Worth: {milestone_weight} pts (out of 100 total)")
                print(f"⚠️ WARNING: Empty or minimal diff detected")
                print(f"Quality: 0% complete")
                print(f"Earned: 0.00/{milestone_weight} pts")
                print(f"Remark: No significant code changes detected")

                # Add to output log with detailed feedback - Teams format
                output_log.append(f"\n## MILESTONE {i}: {milestone['desc']}\n")
                output_log.append(f"**Commit Message:** {commit.message.strip()}")
                output_log.append(f"**Points Worth:** {milestone_weight} pts (out of 100 total)\n")

                output_log.append(f"### 📋 Expected Files:")
                for file in milestone.get('files', []):
                    output_log.append(f"- {file}")

                output_log.append(f"\n### 📋 Grading Criteria:")
                for idx, criterion in enumerate(milestone.get('criteria', []), 1):
                    output_log.append(f"{idx}. {criterion}")

                output_log.append(f"\n### ⚠️ Issue Detected:")
                output_log.append(f"No significant code changes were found in this commit. This milestone appears to be missing or empty.\n")

                output_log.append(f"### 📊 Score:")
                output_log.append(f"- **Quality:** 0% complete")
                output_log.append(f"- **Earned:** 0.00/{milestone_weight} pts\n")

                output_log.append(f"### 💡 Feedback:")
                output_log.append(f"Please ensure you commit meaningful code changes that address the milestone requirements. Review the expected files and criteria above.\n")
                output_log.append("---\n")

                student_scores.append({
                    'milestone_num': i,
                    'quality_score': 0,
                    'weight': milestone_weight,
                    'earned_points': 0,
                    'remark': 'No significant code changes detected'
                })
                continue

            # Test-based grading - checks actual files and code features
            result = test_based_grading(local_path, commit.message, milestone)
            quality_score = result.get('quality_score', 0)
            milestone_weight = milestone.get('weight', 0)

            # Validation: Ensure quality_score is in valid range
            if not isinstance(quality_score, (int, float)) or quality_score < 0 or quality_score > 100:
                print(f"⚠️ Invalid quality score: {quality_score}, setting to 0")
                quality_score = 0

            # Calculate weighted score for this milestone
            # quality_score (0-100) * weight / 100 = points earned
            earned_points = (quality_score / 100.0) * milestone_weight

            student_scores.append({
                'milestone_num': i,
                'quality_score': quality_score,
                'weight': milestone_weight,
                'earned_points': earned_points,
                'remark': result.get('remark', '')
            })

            total_weighted_score += earned_points
            total_possible_weight += milestone_weight

            # Print to console
            print(f"\n{'='*70}")
            print(f"Milestone {i}: {milestone['desc']}")
            print(f"{'='*70}")
            print(f"Commit message: {commit.message.strip()}")
            print(f"Worth: {milestone_weight} pts (out of 100 total)")
            print(f"Quality: {quality_score}% complete")
            print(f"Earned: {earned_points:.2f}/{milestone_weight} pts")
            print(f"Remark: {result.get('remark','')}")

            # Add detailed feedback to output log - Teams format
            output_log.append(f"\n## MILESTONE {i}: {milestone['desc']}\n")
            output_log.append(f"**Commit Message:** {commit.message.strip()}")
            output_log.append(f"**Points Worth:** {milestone_weight} pts (out of 100 total)\n")

            # Expected files section
            output_log.append(f"### 📋 Expected Files:")
            for file in milestone.get('files', []):
                output_log.append(f"- {file}")

            # Grading criteria section
            output_log.append(f"\n### 📋 Grading Criteria:")
            for idx, criterion in enumerate(milestone.get('criteria', []), 1):
                output_log.append(f"{idx}. {criterion}")

            # Get files found/missing info
            found_files, missing_files = check_files_exist(local_path, milestone.get('files', []))

            # Files status section
            output_log.append(f"\n### 📁 Files Status:")
            if found_files:
                output_log.append(f"✅ **Files Found:** {', '.join(found_files)}")
            if missing_files:
                output_log.append(f"❌ **Files Missing:** {', '.join(missing_files)}")

            # Features detected section
            features_found = check_code_features(local_path, milestone)
            if features_found:
                output_log.append(f"\n### 🔍 Implementation Detected:")
                for feature in features_found:
                    output_log.append(f"- ✅ {feature}")

            # Score section
            output_log.append(f"\n### 📊 Score:")
            output_log.append(f"- **Quality:** {quality_score}% complete")
            output_log.append(f"- **Earned:** {earned_points:.2f}/{milestone_weight} pts")

            # Performance indicator
            if quality_score >= 90:
                performance = "🌟 **EXCELLENT!** You've done outstanding work on this milestone."
            elif quality_score >= 75:
                performance = "👍 **GOOD JOB!** Your implementation meets most requirements well."
            elif quality_score >= 60:
                performance = "✓ **ACCEPTABLE.** Your implementation shows understanding but could be improved."
            elif quality_score >= 45:
                performance = "⚠️ **NEEDS IMPROVEMENT.** Review the criteria and enhance your implementation."
            else:
                performance = "❌ **INCOMPLETE.** Significant work needed to meet milestone requirements."

            output_log.append(f"\n### 💬 Assessment:")
            output_log.append(f"{performance}")
            output_log.append(f"{result.get('remark','')}")

            # Suggestions for improvement
            if quality_score < 100:
                output_log.append(f"\n### 💡 Suggestions for Improvement:")
                if missing_files:
                    output_log.append(f"- Create or update the missing files: {', '.join(missing_files)}")
                if quality_score < 80:
                    output_log.append(f"- Review all grading criteria above and ensure each is addressed")
                    output_log.append(f"- Test your implementation thoroughly to ensure it works correctly")
                if quality_score < 60:
                    output_log.append(f"- Consider reviewing course materials related to this milestone")
                    output_log.append(f"- Seek help from instructor or peers if you're stuck")

            output_log.append("\n---\n")

        # ------------------------------
        # Final grade calculation
        # ------------------------------
        if student_scores:
            # Print to console
            print(f"\n\n{'='*70}")
            print(f"📊 FINAL GRADING SUMMARY for {repo.name}")
            print(f"{'='*70}\n")

            # Add to output log with enhanced formatting - Teams format
            output_log.append(f"\n\n# 📊 FINAL GRADING SUMMARY\n")
            output_log.append("This section summarizes your performance across all milestone categories.")
            output_log.append("Review your strengths and areas for improvement below.\n")

            # Group by category for display
            categories = {
                "Basic Setup & Core Features": [1, 2, 3, 4, 5, 6, 7],
                "Security & Validation": [8, 21, 22],
                "Transaction Features": [9, 10, 11, 12],
                "Advanced Features": [13, 14],
                "Admin & Logging": [15, 16, 17],
                "Additional Security": [18, 19, 20]
            }

            output_log.append("## Category Breakdown\n")

            for category_name, milestone_nums in categories.items():
                category_earned = sum([s['earned_points'] for s in student_scores if s['milestone_num'] in milestone_nums])
                category_total = sum([MILESTONES[m]['weight'] for m in milestone_nums if m in MILESTONES])
                if category_total > 0:
                    percentage = (category_earned / category_total * 100) if category_total > 0 else 0

                    # Performance indicator for category
                    if percentage >= 90:
                        indicator = "🌟 Excellent"
                    elif percentage >= 75:
                        indicator = "👍 Good"
                    elif percentage >= 60:
                        indicator = "✓ Acceptable"
                    elif percentage >= 45:
                        indicator = "⚠️ Needs Work"
                    else:
                        indicator = "❌ Incomplete"

                    line = f"**{category_name}:** {category_earned:.2f}/{category_total} pts ({percentage:.1f}%) {indicator}"
                    print(f"{category_name:35} {category_earned:5.2f}/{category_total:2} pts ({percentage:5.1f}%)")
                    output_log.append(line)

            # Calculate bonuses and penalties
            bonuses_penalties = []
            bonus_total = 0

            # Check instruction following bonus (average quality > 80%)
            if student_scores:
                avg_quality = sum([s['quality_score'] for s in student_scores]) / len(student_scores)
                if avg_quality >= INSTRUCTION_THRESHOLD:
                    bonus_total += INSTRUCTION_FOLLOWING_BONUS
                    bonuses_penalties.append(f"✅ Instruction Following Bonus (+{INSTRUCTION_FOLLOWING_BONUS} pts): Average quality {avg_quality:.1f}% ≥ {INSTRUCTION_THRESHOLD}%")
                else:
                    bonuses_penalties.append(f"ℹ️ Instruction Following: Average quality {avg_quality:.1f}% < {INSTRUCTION_THRESHOLD}% (no bonus)")

            # Check late submission penalty
            try:
                deadline = datetime.strptime(SUBMISSION_DEADLINE, "%Y-%m-%d %H:%M:%S")
                if commit_list:
                    last_commit = commit_list[-1]
                    last_commit_date = datetime.fromtimestamp(last_commit.committed_date)

                    if last_commit_date > deadline:
                        bonus_total -= LATE_SUBMISSION_PENALTY
                        days_late = (last_commit_date - deadline).days
                        bonuses_penalties.append(f"⚠️ Late Submission Penalty (-{LATE_SUBMISSION_PENALTY} pts): Submitted {days_late} day(s) late")
                    else:
                        bonuses_penalties.append(f"✅ On-Time Submission: No penalty")
            except Exception as e:
                bonuses_penalties.append(f"ℹ️ Could not verify submission date: {e}")

            # Apply bonuses/penalties
            raw_score = total_weighted_score
            total_weighted_score = max(0, min(100, total_weighted_score + bonus_total))  # Keep score between 0-100

            # Display bonuses/penalties
            if bonuses_penalties:
                output_log.append(f"\n## 🎁 Bonuses & Penalties\n")
                for bp in bonuses_penalties:
                    output_log.append(f"{bp}")

                if bonus_total != 0:
                    output_log.append(f"\n**Adjustment:** {bonus_total:+.1f} pts")
                    output_log.append(f"**Score before adjustment:** {raw_score:.2f} pts")
                    output_log.append(f"**Score after adjustment:** {total_weighted_score:.2f} pts")

            # Total score line
            output_log.append(f"\n---\n")
            output_log.append(f"### **FINAL TOTAL SCORE: {total_weighted_score:.2f}/100 pts**")
            output_log.append(f"---\n")

            print(f"\n{'-'*70}")
            if bonus_total != 0:
                print(f"{'RAW SCORE:':35} {raw_score:5.2f}/100 pts")
                print(f"{'ADJUSTMENT:':35} {bonus_total:+5.2f} pts")
            print(f"{'FINAL TOTAL SCORE:':35} {total_weighted_score:5.2f}/100 pts")
            print(f"{'-'*70}")

            # Letter grade with detailed feedback
            if total_weighted_score >= 80:
                grade = "A (Excellent)"
                grade_emoji = "🌟"
                grade_feedback = "Outstanding work! You have demonstrated excellent understanding and implementation of the project requirements."
                next_steps = "Continue maintaining this high level of quality in your future projects."
            elif total_weighted_score >= 75:
                grade = "B+ (Very Good)"
                grade_emoji = "🎯"
                grade_feedback = "Very good work! You have a strong grasp of the concepts with minor areas for improvement."
                next_steps = "Review the areas marked for improvement to achieve excellence."
            elif total_weighted_score >= 70:
                grade = "B (Good)"
                grade_emoji = "👍"
                grade_feedback = "Good work! You have demonstrated solid understanding of the core concepts."
                next_steps = "Focus on implementing more advanced features and improving code quality."
            elif total_weighted_score >= 65:
                grade = "C+ (Fairly Good)"
                grade_emoji = "✓"
                grade_feedback = "Fairly good effort! You have grasped the basic concepts but need to strengthen your implementation."
                next_steps = "Review the feedback on each milestone and work on completing missing requirements."
            elif total_weighted_score >= 60:
                grade = "C (Fair)"
                grade_emoji = "⚠️"
                grade_feedback = "Fair work. You have shown basic understanding but significant improvements are needed."
                next_steps = "Review course materials, complete missing milestones, and seek help if needed."
            elif total_weighted_score >= 55:
                grade = "D+ (Poor)"
                grade_emoji = "❗"
                grade_feedback = "Your work needs significant improvement. Many requirements are incomplete or missing."
                next_steps = "Schedule time with your instructor to review the project requirements and get guidance."
            elif total_weighted_score >= 50:
                grade = "D (Very Poor)"
                grade_emoji = "❌"
                grade_feedback = "Your submission is incomplete and does not meet the minimum requirements."
                next_steps = "Meet with your instructor immediately to discuss how to improve your work."
            else:
                grade = "F (Fail)"
                grade_emoji = "⛔"
                grade_feedback = "Your submission does not meet the basic requirements of this project."
                next_steps = "You must redo this project. Please consult with your instructor for guidance."

            # Print to console
            print(f"\n🏆 FINAL GRADE: {grade}")
            print(f"{'='*70}\n")

            # Detailed output to log - Teams format
            output_log.append(f"\n## {grade_emoji} FINAL GRADE: {grade}\n")

            output_log.append(f"### 📝 Overall Assessment")
            output_log.append(f"{grade_feedback}\n")

            output_log.append(f"### 🎯 Next Steps")
            output_log.append(f"{next_steps}\n")

            # Identify strengths and weaknesses
            output_log.append(f"### 💪 Strengths")
            strong_milestones = [s for s in student_scores if s['quality_score'] >= 80]
            if strong_milestones:
                for s in strong_milestones[:3]:  # Show top 3
                    ms = MILESTONES[s['milestone_num']]
                    output_log.append(f"- ✓ Milestone {s['milestone_num']}: {ms['desc']} ({s['quality_score']}%)")
            else:
                output_log.append(f"- No milestones scored above 80%. Focus on improving overall implementation.")

            output_log.append(f"\n### 📌 Areas for Improvement")
            weak_milestones = [s for s in student_scores if s['quality_score'] < 70]
            if weak_milestones:
                for s in weak_milestones[:5]:  # Show top 5 weakest
                    ms = MILESTONES[s['milestone_num']]
                    output_log.append(f"- Milestone {s['milestone_num']}: {ms['desc']} ({s['quality_score']}% - needs work)")
            else:
                output_log.append(f"- Good job! All completed milestones scored above 70%.")

            # Statistics
            completed_milestones = len([s for s in student_scores if s['quality_score'] >= 50])
            total_milestones = len(student_scores)
            avg_quality_calc = sum([s['quality_score'] for s in student_scores]) / len(student_scores) if student_scores else 0

            output_log.append(f"\n### 📈 Statistics")
            output_log.append(f"- **Milestones Completed:** {completed_milestones}/{total_milestones} ({(completed_milestones/total_milestones*100):.1f}%)")
            output_log.append(f"- **Average Quality Score:** {avg_quality_calc:.1f}%")
            output_log.append(f"- **Raw Points Earned:** {raw_score:.2f}/100")
            if bonus_total != 0:
                output_log.append(f"- **Bonus/Penalty Applied:** {bonus_total:+.2f} pts")
            output_log.append(f"- **Final Total Points:** {total_weighted_score:.2f}/100\n")

            output_log.append(f"---\n")
            output_log.append(f"**End of Grading Report**\n")
            output_log.append(f"If you have questions about your grade, please review this report carefully and consult with your instructor during office hours.\n")

            # Write to result.txt file
            try:
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_log))
                print(f"✅ Results saved to: {result_file}")
            except Exception as e:
                print(f"⚠️ Failed to write result file: {e}")

            # Collect student summary information
            student_summary.append({
                'repo_name': repo.name,
                'github_username': student_github_username,
                'final_score': total_weighted_score,
                'grade': grade
            })

        else:
            print("⚠️ No milestones graded for this repo.")
            output_log.append("\n## ⚠️ No Milestones Graded\n")
            output_log.append("No milestones were found or graded for this repository.")
            output_log.append("Please ensure your repository has commits corresponding to the project milestones.\n")
            try:
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(output_log))
            except Exception as e:
                print(f"⚠️ Failed to write result file: {e}")

            # Collect student summary even if no milestones graded
            student_summary.append({
                'repo_name': repo.name,
                'github_username': student_github_username,
                'final_score': 0.0,
                'grade': "No submissions"
            })

    except GitCommandError as e:
        print(f"❌ Git error for {repo.name}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error for {repo.name}: {e}")

# ------------------------------
# WRITE STUDENT SUMMARY FILE
# ------------------------------
if student_summary:
    summary_file = os.path.join(OUTPUT_DIR, "student_summary.txt")
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("STUDENT GRADING SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            for student in student_summary:
                f.write(f"Repository: {student['repo_name']}\n")
                f.write(f"GitHub Username: @{student['github_username']}\n")
                f.write(f"Final Score: {student['final_score']:.2f}/100\n")
                f.write(f"Grade: {student['grade']}\n")
                f.write("-"*80 + "\n\n")

        print(f"\n\n✅ Student summary saved to: {summary_file}")
        print(f"📊 Total students graded: {len(student_summary)}")
    except Exception as e:
        print(f"⚠️ Failed to write student summary: {e}")