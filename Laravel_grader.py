# laravel_grader.py
# General Laravel Auto-Grader (for Event Management System or similar projects)

import os, re, json, io, sys
import argparse
from pathlib import Path
from git import Repo
from github import Github
from datetime import datetime
from openai import OpenAI
import requests

# Import test runner
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Laravel'))
    from copy_and_run_tests import LaravelTestRunner
    TEST_RUNNER_AVAILABLE = False  # ⭐ TEMPORARILY DISABLED - PHP/Composer not available
    print("[INFO] Functionality tests disabled. Using static analysis only.")
except ImportError:
    TEST_RUNNER_AVAILABLE = False
    print("[WARNING] Test runner not available. Install requirements or check Laravel/copy_and_run_tests.py")

# --- CONFIG ---
from config import (
    GITHUB_TOKEN, ORG_NAME,
    LARAVEL_ASSIGNMENT_REPO_PREFIX as ASSIGNMENT_REPO_PREFIX,
    LARAVEL_MOODLE_COURSE_ID, LARAVEL_MOODLE_ACTIVITY_ID, LARAVEL_MOODLE_GRADE_ITEM_ID,
    OPENAI_API_KEY, OUTPUT_DIR, MODEL_NAME, MOODLE_URL, MOODLE_TOKEN
)

client = OpenAI(api_key=OPENAI_API_KEY)

g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)

# --- RUBRIC ---
RUBRIC = {
    "Models": 15,
    "Controllers": 15,
    "Migrations": 10,
    "Routes": 8,
    "Views": 8,
    "Constraint Logic": 10,
    "Documentation": 8,
    "Commits": 10,
    "Functionality Tests": 30,  # PHPUnit tests (if available)
}

# Rubric without tests (for fallback when tests can't run)
RUBRIC_NO_TESTS = {
    "Models": 20,
    "Controllers": 20,
    "Migrations": 15,
    "Routes": 10,
    "Views": 10,
    "Constraint Logic": 15,
    "Documentation": 10,
    "Commits": 15,
}

# --- CHECK FUNCTIONS ---

def is_laravel_project(path):
    """Check if a directory contains a Laravel project"""
    # Check for key Laravel indicators
    artisan_path = os.path.join(path, 'artisan')
    composer_path = os.path.join(path, 'composer.json')
    public_index_path = os.path.join(path, 'public', 'index.php')
    
    # At least one of these must exist
    if os.path.exists(artisan_path):
        return True
    if os.path.exists(composer_path):
        # Verify it's actually a Laravel project by checking composer.json content
        try:
            with open(composer_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'laravel/framework' in content:
                    return True
        except:
            pass
    if os.path.exists(public_index_path):
        # Check if index.php contains Laravel-specific code
        try:
            with open(public_index_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'laravel' in content or 'kernel' in content:
                    return True
        except:
            pass
    
    return False

def find_laravel_project(root_path, max_depth=5):
    """
    Recursively search for a Laravel project in the directory tree.
    
    Args:
        root_path: The root directory to start searching from
        max_depth: Maximum depth to search (default 5 to prevent excessive recursion)
    
    Returns:
        Path to Laravel project directory if found, None otherwise
    """
    def search_recursive(current_path, depth=0):
        if depth > max_depth:
            return None
        
        # Check if current directory is a Laravel project
        if is_laravel_project(current_path):
            print(f"[FOUND] Laravel project at: {current_path}")
            return current_path
        
        # Search subdirectories
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                
                # Skip common non-project directories
                skip_dirs = {'.git', 'node_modules', 'vendor', 'storage', '__pycache__', 
                           '.idea', '.vscode', 'venv', 'env', '.env'}
                if item in skip_dirs:
                    continue
                
                if os.path.isdir(item_path):
                    result = search_recursive(item_path, depth + 1)
                    if result:
                        return result
        except (PermissionError, OSError) as e:
            print(f"[WARNING] Cannot access {current_path}: {e}")
        
        return None
    
    print(f"[SEARCHING] Looking for Laravel project in: {root_path}")
    laravel_path = search_recursive(root_path)
    
    if laravel_path:
        return laravel_path
    else:
        print(f"[ERROR] No Laravel project found in {root_path}")
        return None

def read_file(path):
    try:
        return open(path, encoding='utf-8', errors='ignore').read().lower()
    except:
        return ''

def check_models(base):
    model_dir = os.path.join(base, 'app', 'Models')
    if not os.path.exists(model_dir):
        return 0, ['Models directory missing']
    score, remarks = 0, []
    for f in os.listdir(model_dir):
        if not f.endswith('.php'): continue
        content = read_file(os.path.join(model_dir, f))
        if any(x in content for x in ['hasmany', 'belongsto', 'belongstomany']):
            score += 6
            remarks.append(f'Relationships found in {f}')
        if 'fillable' in content or 'guarded' in content:
            score += 4
            remarks.append(f'Fillable/guarded defined in {f}')
    return min(score, RUBRIC['Models']), remarks

def check_controllers(base):
    ctrl_dir = os.path.join(base, 'app', 'Http', 'Controllers')
    score, remarks = 0, []
    for root, _, files in os.walk(ctrl_dir):
        for f in files:
            if not f.endswith('.php'): continue
            content = read_file(os.path.join(root, f))
            if '$request->validate' in content: score += 5
            if 'overlap' in content or 'conflict' in content: score += 5
            if 'capacity' in content: score += 5
            if 'open_time' in content or 'close_time' in content: score += 5
            remarks.append(f'Checked controller: {f}')
    return min(score, RUBRIC['Controllers']), remarks

def check_migrations(base):
    mdir = os.path.join(base, 'database', 'migrations')
    if not os.path.exists(mdir):
        return 0, ['No migrations found']
    score, remarks = 0, []
    for f in os.listdir(mdir):
        content = read_file(os.path.join(mdir, f))
        if 'foreignid' in content: score += 3
        if 'capacity' in content or 'participants' in content: score += 3
        if 'timestamps' in content: score += 2
        if 'schema::create' in content: score += 3
        remarks.append(f'Checked migration: {f}')
    return min(score, RUBRIC['Migrations']), remarks

def check_routes(base):
    route_file = os.path.join(base, 'routes', 'web.php')
    if not os.path.exists(route_file): return 0, ['web.php missing']
    content = read_file(route_file)
    score = 0
    if 'route::resource' in content or 'route::get' in content: score += 5
    if 'controller' in content: score += 5
    return min(score, RUBRIC['Routes']), ['Routes checked']

def check_views(base):
    """Check for views in multiple locations"""
    score = 0
    remarks = []
    view_files_found = 0
    
    # Check traditional blade templates in resources/views
    vdir = os.path.join(base, 'resources', 'views')
    if os.path.exists(vdir):
        for root, _, files in os.walk(vdir):
            for f in files:
                if f.endswith('.blade.php'):
                    score += 2
                    view_files_found += 1
        if view_files_found > 0:
            remarks.append(f'{view_files_found} Blade templates in resources/views')
    
    # Check for modern JS frameworks in resources/js
    jsdir = os.path.join(base, 'resources', 'js')
    js_view_count = 0
    if os.path.exists(jsdir):
        for root, _, files in os.walk(jsdir):
            for f in files:
                # Check for Vue, React, or Svelte components
                if f.endswith(('.vue', '.jsx', '.tsx', '.svelte')):
                    score += 2
                    js_view_count += 1
                    view_files_found += 1
        if js_view_count > 0:
            remarks.append(f'{js_view_count} JS framework components in resources/js')
    
    # Check for HTML files anywhere in resources
    resources_dir = os.path.join(base, 'resources')
    html_count = 0
    if os.path.exists(resources_dir):
        for root, _, files in os.walk(resources_dir):
            for f in files:
                if f.endswith('.html') and 'node_modules' not in root:
                    score += 1  # Less points for plain HTML
                    html_count += 1
                    view_files_found += 1
        if html_count > 0:
            remarks.append(f'{html_count} HTML files in resources')
    
    # Finalize score
    score = min(score, RUBRIC_NO_TESTS.get('Views', 10))  # Use fallback rubric value
    
    if view_files_found == 0:
        return 0, ['No view templates found in resources/views or resources/js']
    
    return score, remarks

def check_readme(base):
    """
    Check for README documentation at multiple levels.
    Supports different project structures:
    - Root level: event-scheduler-student/README.md
    - Backend folder: event-scheduler-student/backend/README.md
    - Subfolder: event-scheduler-student/event-management-system/README.md
    """
    # Check multiple possible locations for README files
    readme_paths = [
        os.path.join(base, 'README.md'),                    # Laravel project directory
        os.path.join(base, '..', 'README.md'),              # Repository root (one level up)
        os.path.join(base, '..', '..', 'README.md'),        # Two levels up (for deeply nested projects)
    ]
    
    content = ''
    readme_locations = []
    
    for path in readme_paths:
        if os.path.exists(path):
            # Avoid reading the same file twice (different paths to same file)
            real_path = os.path.realpath(path)
            if real_path not in readme_locations:
                readme_content = read_file(path)
                content += readme_content + ' '
                readme_locations.append(real_path)
    
    if not readme_locations:
        return 0, ['README.md missing (checked Laravel dir and repository root)']
    
    # Score based on project-specific documentation keywords
    score = 0
    remarks = []
    
    if 'overlap' in content or 'conflict' in content or 'double-book' in content:
        score += 3
        remarks.append('Time overlap logic documented')
    
    if 'capacity' in content or 'participant' in content or 'attendee' in content:
        score += 3
        remarks.append('Capacity constraints documented')
    
    if 'reflection' in content or 'challenge' in content or 'lesson' in content:
        score += 2
        remarks.append('Reflection/learning notes included')
    
    if 'screenshot' in content or '.png' in content or '.jpg' in content or 'image' in content:
        score += 2
        remarks.append('Screenshots/images referenced')
    
    if not remarks:
        remarks.append('README found but lacks project-specific documentation')
    
    return min(score, RUBRIC['Documentation']), remarks

def check_constraint_logic(base):
    logic_score, remarks = 0, []
    for root, _, files in os.walk(base):
        for f in files:
            if not f.endswith('.php'): continue
            content = read_file(os.path.join(root, f))
            if 'start_time' in content and 'end_time' in content and '>' in content: logic_score += 5
            if 'capacity' in content and '<=' in content: logic_score += 5
            if 'open_time' in content and 'close_time' in content: logic_score += 5
    return min(logic_score, RUBRIC['Constraint Logic']), ['Constraint logic detected']

def check_commits(repo):
    commits = list(repo.iter_commits())
    score = min(len(commits), 10) + 5 if any('fix' in c.message.lower() for c in commits) else 0
    return min(score, RUBRIC['Commits']), [f'{len(commits)} commits analyzed']

# --- HTML REPORT GENERATION ---

def generate_html_report(repo_name, results, total_score, local_path, tests_ran=False):
    """Generate HTML report for Laravel grading"""
    # Use appropriate rubric based on whether tests ran
    current_rubric = RUBRIC if tests_ran else RUBRIC_NO_TESTS
    
    output = []
    output.append('<!DOCTYPE html>')
    output.append('<html><head><meta charset="UTF-8">')
    output.append('<title>Laravel Grading Report</title>')
    output.append('<style>')
    output.append('body { font-family: Arial, sans-serif; max-width: 900px; margin: 20px auto; padding: 20px; background: #f5f5f5; }')
    output.append('.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }')
    output.append('.header h1 { margin: 0 0 15px 0; font-size: 2em; }')
    output.append('.header p { margin: 5px 0; opacity: 0.9; }')
    output.append('.category { background: #fff; margin: 15px 0; padding: 20px; border-left: 4px solid #667eea; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }')
    output.append('.category h2 { margin-top: 0; color: #333; font-size: 1.5em; }')
    output.append('.category ul { margin: 10px 0; padding-left: 20px; }')
    output.append('.category li { margin: 5px 0; color: #555; }')
    output.append('.score-excellent { color: #28a745; font-weight: bold; font-size: 1.2em; }')
    output.append('.score-good { color: #17a2b8; font-weight: bold; font-size: 1.2em; }')
    output.append('.score-fair { color: #ffc107; font-weight: bold; font-size: 1.2em; }')
    output.append('.score-poor { color: #dc3545; font-weight: bold; font-size: 1.2em; }')
    output.append('.final-score { background: #fff; padding: 25px; border-radius: 8px; text-align: center; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }')
    output.append('.final-score h2 { margin: 0; font-size: 2.5em; }')
    output.append('.ai-review { background: #f8f9fa; border-left: 4px solid #764ba2; }')
    output.append('.ai-review .summary { background: #fff; padding: 15px; margin: 10px 0; border-radius: 4px; }')
    output.append('.ai-review .suggestions { background: #fff; padding: 15px; margin: 10px 0; border-radius: 4px; }')
    output.append('.progress-bar { background: #e9ecef; border-radius: 10px; height: 20px; margin: 10px 0; overflow: hidden; }')
    output.append('.progress-fill { height: 100%; transition: width 0.3s ease; }')
    output.append('.progress-excellent { background: linear-gradient(90deg, #28a745, #20c997); }')
    output.append('.progress-good { background: linear-gradient(90deg, #17a2b8, #20c997); }')
    output.append('.progress-fair { background: linear-gradient(90deg, #ffc107, #fd7e14); }')
    output.append('.progress-poor { background: linear-gradient(90deg, #dc3545, #c82333); }')
    output.append('</style></head><body>')
    
    output.append('<div class="header">')
    output.append(f'<h1>🎓 Laravel Project Grading Report</h1>')
    output.append(f'<p><strong>Repository:</strong> {repo_name}</p>')
    output.append(f'<p><strong>Graded on:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
    output.append('</div>')
    
    # Categories with scores
    for category, details in results.items():
        if category == "AI Review":
            output.append('<div class="category ai-review">')
            output.append(f'<h2>🤖 AI Review</h2>')
            output.append(f'<div class="summary"><strong>Summary:</strong><br>{details.get("summary", "N/A")}</div>')
            suggestions = details.get("suggestions", [])
            if suggestions:
                output.append(f'<div class="suggestions"><strong>Suggestions:</strong><ul>')
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        output.append(f'<li>{suggestion}</li>')
                else:
                    output.append(f'<li>{suggestions}</li>')
                output.append('</ul></div>')
            output.append('</div>')
        elif category == "Functionality Tests":
            # Special handling for functionality tests
            score = details.get('score', 0)
            max_score = details.get('max_score', RUBRIC.get(category, 30))
            test_passed = details.get('test_passed', 0)
            test_total = details.get('test_total', 0)
            test_failed = details.get('test_failed', 0)
            pass_rate = details.get('pass_rate', '0%')
            
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            if percentage >= 80:
                score_class = 'score-excellent'
                progress_class = 'progress-excellent'
            elif percentage >= 60:
                score_class = 'score-good'
                progress_class = 'progress-good'
            elif percentage >= 40:
                score_class = 'score-fair'
                progress_class = 'progress-fair'
            else:
                score_class = 'score-poor'
                progress_class = 'progress-poor'
            
            output.append('<div class="category" style="border-left-color: #28a745;">')
            output.append(f'<h2>🧪 {category}</h2>')
            output.append(f'<p class="{score_class}">Score: {score}/{max_score} pts ({percentage:.1f}%)</p>')
            output.append(f'<p><strong>PHPUnit Tests:</strong> {test_passed}/{test_total} passed ({pass_rate})</p>')
            if test_failed > 0:
                output.append(f'<p style="color: #dc3545;"><strong>Failed:</strong> {test_failed} tests</p>')
            output.append(f'<div class="progress-bar"><div class="progress-fill {progress_class}" style="width: {percentage}%;"></div></div>')
            
            if details.get('remarks'):
                output.append('<ul>')
                for remark in details.get('remarks', []):
                    output.append(f'<li>{remark}</li>')
                output.append('</ul>')
            output.append('</div>')
        else:
            score = details.get('score', 0)
            # Use the correct rubric that was actually used for grading
            max_score = current_rubric.get(category, 0)
            percentage = (score / max_score * 100) if max_score > 0 else 0
            
            if percentage >= 80:
                score_class = 'score-excellent'
                progress_class = 'progress-excellent'
            elif percentage >= 60:
                score_class = 'score-good'
                progress_class = 'progress-good'
            elif percentage >= 40:
                score_class = 'score-fair'
                progress_class = 'progress-fair'
            else:
                score_class = 'score-poor'
                progress_class = 'progress-poor'
            
            output.append('<div class="category">')
            output.append(f'<h2>{category}</h2>')
            output.append(f'<p class="{score_class}">Score: {score}/{max_score} pts ({percentage:.1f}%)</p>')
            output.append(f'<div class="progress-bar"><div class="progress-fill {progress_class}" style="width: {percentage}%;"></div></div>')
            
            if details.get('remarks'):
                output.append('<ul>')
                for remark in details.get('remarks', []):
                    output.append(f'<li>{remark}</li>')
                output.append('</ul>')
            output.append('</div>')
    
    # Final score
    if total_score >= 80:
        score_class = 'score-excellent'
        emoji = '🌟'
        grade = 'A'
    elif total_score >= 60:
        score_class = 'score-good'
        emoji = '👍'
        grade = 'B'
    elif total_score >= 40:
        score_class = 'score-fair'
        emoji = '⚠️'
        grade = 'C'
    else:
        score_class = 'score-poor'
        emoji = '📝'
        grade = 'D'
    
    output.append(f'<div class="final-score">')
    output.append(f'<h2 class="{score_class}">{emoji} FINAL SCORE: {total_score}/100</h2>')
    output.append(f'<p style="font-size: 1.5em; margin: 10px 0;">Grade: <strong>{grade}</strong></p>')
    output.append('</div>')
    
    output.append('</body></html>')
    
    # Write to file
    report_path = os.path.join(local_path, 'result.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    return report_path

# --- AI FEEDBACK ---

def ai_feedback(base):
    prompt = f"""
    You are grading a Laravel project. Review these folders and files:
    {os.listdir(base)}
    Identify strengths and weaknesses in:
    - Model relationships and fillables
    - Controller validation and logic
    - Migrations and schema design
    - Constraint logic (time overlap, capacity, open/close time)
    Respond in JSON with 'summary' and 'suggestions'.
    """
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except:
        return {"summary": "AI feedback error", "suggestions": []}

# --- TEAMS NOTIFICATION ---

def send_teams_notification(repo_name, score, html_report_path):
    """Send notification to Microsoft Teams about grading completion"""
    try:
        # Check if Teams webhook URL is configured
        teams_webhook = os.getenv('TEAMS_WEBHOOK_URL')
        if not teams_webhook:
            print("[SKIP] Teams webhook not configured (set TEAMS_WEBHOOK_URL environment variable)")
            return False
        
        # Extract student name from repo
        student_name = repo_name.replace(ASSIGNMENT_REPO_PREFIX, "")
        
        # Determine grade color and emoji
        if score >= 90:
            grade_letter = "A"
            color = "28a745"  # Green
            emoji = "🌟"
        elif score >= 80:
            grade_letter = "B"
            color = "17a2b8"  # Blue
            emoji = "👍"
        elif score >= 70:
            grade_letter = "C"
            color = "ffc107"  # Yellow
            emoji = "⚠️"
        elif score >= 60:
            grade_letter = "D"
            color = "fd7e14"  # Orange
            emoji = "📝"
        else:
            grade_letter = "F"
            color = "dc3545"  # Red
            emoji = "❌"
        
        # Create Teams message card
        message = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Grade for {student_name}",
            "themeColor": color,
            "title": f"{emoji} Laravel Project Graded - {student_name}",
            "sections": [
                {
                    "facts": [
                        {"name": "Student:", "value": student_name},
                        {"name": "Repository:", "value": repo_name},
                        {"name": "Score:", "value": f"{score}/100"},
                        {"name": "Grade:", "value": grade_letter},
                        {"name": "Graded on:", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    ]
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Report",
                    "targets": [
                        {"os": "default", "uri": f"file:///{html_report_path.replace(os.sep, '/')}"}
                    ]
                }
            ]
        }
        
        # Send to Teams
        response = requests.post(teams_webhook, json=message, timeout=10)
        
        if response.status_code == 200:
            print(f"[TEAMS] ✓ Notification sent to Teams for {student_name}")
            return True
        else:
            print(f"[TEAMS] ✗ Failed to send notification: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[TEAMS] Error sending notification: {e}")
        return False

# --- MOODLE INTEGRATION ---

def upload_grade_to_moodle(student_username, score, repo_name):
    """Upload grade to Moodle gradebook"""
    try:
        # Check if Moodle is configured
        if not MOODLE_URL or not MOODLE_TOKEN:
            print("[SKIP] Moodle not configured")
            return False
        
        # Import MoodleIntegration if available
        try:
            from MoodleIntegration import MoodleIntegration
        except ImportError:
            print("[SKIP] MoodleIntegration module not available")
            return False
        
        # Initialize Moodle integration
        moodle = MoodleIntegration(
            MOODLE_URL,
            MOODLE_TOKEN,
            LARAVEL_MOODLE_COURSE_ID,
            LARAVEL_MOODLE_ACTIVITY_ID,
            LARAVEL_MOODLE_GRADE_ITEM_ID
        )
        
        # Find student by username (GitHub username)
        print(f"[MOODLE] Looking up student: {student_username}")
        student = moodle.find_student_by_username(student_username)
        
        if not student:
            print(f"[MOODLE] ✗ Student not found in Moodle: {student_username}")
            return False
        
        student_id = student['id']
        
        # Upload grade
        print(f"[MOODLE] Uploading grade {score}/100 for {student_username}...")
        result = moodle.update_grade(student_id, score)
        
        if result:
            print(f"[MOODLE] ✓ Grade uploaded successfully")
            
            # Log the upload
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {student_username} | {repo_name} | {score}/100\n"
            with open('moodle_grade_log.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            return True
        else:
            print(f"[MOODLE] ✗ Failed to upload grade")
            return False
            
    except Exception as e:
        print(f"[MOODLE] Error uploading grade: {e}")
        import traceback
        traceback.print_exc()
        return False

# --- FUNCTIONALITY TESTING ---

def run_functionality_tests(laravel_path):
    """
    Run PHPUnit tests on the Laravel project and return results
    
    Args:
        laravel_path: Path to the Laravel project directory
    
    Returns:
        dict: Test results with score and remarks, or None if tests couldn't run
    """
    if not TEST_RUNNER_AVAILABLE:
        print("[SKIP] Test runner not available")
        return None
    
    try:
        print("\n[TESTING] Running PHPUnit functionality tests...")
        
        # Path to test suite
        test_suite_path = Path(__file__).parent / 'Laravel' / 'tests'
        
        if not test_suite_path.exists():
            print(f"[SKIP] Test suite not found at: {test_suite_path}")
            return None
        
        # Create test runner and execute tests
        runner = LaravelTestRunner(test_suite_path, Path(laravel_path))
        report = runner.run_full_test_suite()
        
        if report and report['summary']['total_tests'] > 0:
            score = report['summary']['score']
            passed = report['summary']['passed']
            total = report['summary']['total_tests']
            failed = report['summary']['failed']
            
            return {
                'score': score,
                'max_score': 100,
                'passed': passed,
                'total': total,
                'failed': failed,
                'remarks': [
                    f"✓ {passed} tests passed",
                    f"✗ {failed} tests failed" if failed > 0 else "All tests passed!",
                    f"Pass rate: {score}%"
                ],
                'details': report.get('test_details', [])
            }
        else:
            print("[SKIP] Tests could not run or no tests executed")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to run functionality tests: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- MAIN ---

def grade_project(repo, path):
    results = {}
    total = 0
    
    # Try to run functionality tests first
    test_results = run_functionality_tests(path)
    tests_ran = test_results is not None
    
    # Choose appropriate rubric based on whether tests ran
    current_rubric = RUBRIC if tests_ran else RUBRIC_NO_TESTS
    max_possible = sum(current_rubric.values())
    
    print(f"\n[GRADING] Using rubric: {'WITH' if tests_ran else 'WITHOUT'} functionality tests")
    print(f"[INFO] Maximum possible points: {max_possible}")
    
    funcs = [
        ("Models", check_models),
        ("Controllers", check_controllers),
        ("Migrations", check_migrations),
        ("Routes", check_routes),
        ("Views", check_views),
        ("Constraint Logic", check_constraint_logic),
        ("Documentation", check_readme),
    ]
    for name, func in funcs:
        score, remarks = func(path)
        total += score
        results[name] = {"score": score, "remarks": remarks}

    commit_score, remarks = check_commits(repo)
    total += commit_score
    results['Commits'] = {"score": commit_score, "remarks": remarks}

    # Add functionality test results if available
    if tests_ran and test_results:
        # Calculate weighted score based on RUBRIC
        functionality_weight = current_rubric.get('Functionality Tests', 30)
        test_score = round((test_results['score'] / 100) * functionality_weight)
        
        results['Functionality Tests'] = {
            "score": test_score,
            "max_score": functionality_weight,
            "test_passed": test_results['passed'],
            "test_total": test_results['total'],
            "test_failed": test_results['failed'],
            "pass_rate": f"{test_results['score']}%",
            "remarks": test_results['remarks']
        }
        total += test_score
        print(f"[TEST SCORE] {test_results['passed']}/{test_results['total']} tests passed = {test_score}/{functionality_weight} points")

    ai = ai_feedback(path)
    results['AI Review'] = ai

    # Scale the score to 100 points proportionally
    # Instead of capping at 100, convert to percentage of max possible
    final_score = round((total / max_possible) * 100)
    
    return final_score, results, tests_ran

# --- EXECUTION ---

def main(update_repos=False, student_filter=None, skip_teams=False, skip_moodle=False):
    """
    Main grading function.
    
    Args:
        update_repos: If True, pull latest changes for existing repos. 
                     If False (default), skip pulling and use existing code.
        student_filter: List of GitHub usernames to grade. If None, grade all students.
        skip_teams: If True, skip sending Teams notifications.
        skip_moodle: If True, skip uploading grades to Moodle.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    repos = [r for r in org.get_repos() if r.name.startswith(ASSIGNMENT_REPO_PREFIX)]
    
    # Filter repos if student_filter is provided
    if student_filter:
        filtered_repos = []
        for repo in repos:
            student_username = repo.name.replace(ASSIGNMENT_REPO_PREFIX, "")
            if student_username in student_filter:
                filtered_repos.append(repo)
        repos = filtered_repos
        print(f"\n[FILTER] Grading only {len(repos)} student(s): {', '.join(student_filter)}")
        if len(repos) == 0:
            print("[ERROR] No matching repositories found for the specified students!")
            print(f"[INFO] Looking for repos starting with: {ASSIGNMENT_REPO_PREFIX}")
            return
    
    for repo in repos:
        print(f'\n{"="*70}')
        print(f'Grading {repo.name}...')
        print("="*70)
        
        local_path = os.path.join(OUTPUT_DIR, repo.name)
        
        # Clone or pull repo
        if not os.path.exists(local_path):
            print(f"[CLONING] {repo.clone_url}")
            try:
                Repo.clone_from(repo.clone_url.replace('https://', f'https://{GITHUB_TOKEN}@'), local_path)
            except Exception as e:
                print(f"[ERROR] Failed to clone: {e}")
                continue
        else:
            if update_repos:
                print(f"[EXISTS] Repository already cloned, pulling latest changes...")
                try:
                    r = Repo(local_path)
                    r.remotes.origin.pull()
                    print(f"[UPDATED] Successfully pulled latest changes")
                except Exception as e:
                    print(f"[WARNING] Could not pull latest changes: {e}")
            else:
                print(f"[EXISTS] Repository already cloned, using existing code (use --update to pull latest changes)")
        
        # Find Laravel project (might be in subdirectory)
        laravel_path = find_laravel_project(local_path)
        
        if not laravel_path:
            print(f"[SKIP] No Laravel project found in {repo.name}")
            continue
        
        # Grade the project
        try:
            r = Repo(local_path)
            score, results, tests_ran = grade_project(r, laravel_path)
            
            print(f'\n[RESULT] Final Score: {score}/100')
            
            # Save JSON report in the Laravel project directory
            json_path = os.path.join(laravel_path, 'grading_result.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f'[SAVED] JSON report: {json_path}')
            
            # Generate HTML report in the Laravel project directory
            html_report = generate_html_report(repo.name, results, score, laravel_path, tests_ran)
            print(f'[SAVED] HTML report: {html_report}')
            
            # Extract student username from repo name
            student_username = repo.name.replace(ASSIGNMENT_REPO_PREFIX, "")
            
            # Send Teams notification (unless skipped)
            if not skip_teams:
                print(f'\n[NOTIFICATION] Sending notifications for {student_username}...')
                send_teams_notification(repo.name, score, html_report)
            else:
                print(f'\n[SKIP] Teams notification skipped for {student_username}')
            
            # Upload grade to Moodle (unless skipped)
            if not skip_moodle:
                upload_grade_to_moodle(student_username, score, repo.name)
            else:
                print(f'[SKIP] Moodle upload skipped for {student_username}')
            
        except Exception as e:
            print(f"[ERROR] Failed to grade project: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f'\n{"="*70}')
    print("Grading complete!")
    print("="*70)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Grade Laravel projects from GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Grade all students
  python Laravel_grader.py              # Grade using existing repos (no pull)
  python Laravel_grader.py --update     # Grade and pull latest changes
  
  # Grade specific students only
  python Laravel_grader.py --students ndrewpk p-e-koko
  python Laravel_grader.py -s glad1223 --update
  
  # Skip notifications/uploads
  python Laravel_grader.py --skip-teams              # Grade but don't send Teams messages
  python Laravel_grader.py --skip-moodle             # Grade but don't upload to Moodle
  python Laravel_grader.py --skip-teams --skip-moodle  # Only generate reports
  
  # Combine filters (re-grade one student and send only Teams notification)
  python Laravel_grader.py -s p-e-koko --skip-moodle --update
        '''
    )
    parser.add_argument(
        '--update', '--pull', '-u',
        action='store_true',
        dest='update_repos',
        help='Pull latest changes from GitHub for existing repositories'
    )
    parser.add_argument(
        '--students', '-s',
        nargs='+',
        dest='student_filter',
        metavar='USERNAME',
        help='Grade only specific students (provide GitHub usernames without repo prefix)'
    )
    parser.add_argument(
        '--skip-teams',
        action='store_true',
        dest='skip_teams',
        help='Skip sending Teams notifications'
    )
    parser.add_argument(
        '--skip-moodle',
        action='store_true',
        dest='skip_moodle',
        help='Skip uploading grades to Moodle'
    )
    
    args = parser.parse_args()
    main(
        update_repos=args.update_repos,
        student_filter=args.student_filter,
        skip_teams=args.skip_teams,
        skip_moodle=args.skip_moodle
    )
