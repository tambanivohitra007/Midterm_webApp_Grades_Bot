# laravel_grader.py
# General Laravel Auto-Grader (for Event Management System or similar projects)

import os, re, json, io, sys
from git import Repo
from github import Github
from datetime import datetime
from openai import OpenAI

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
    vdir = os.path.join(base, 'resources', 'views')
    if not os.path.exists(vdir): return 0, ['No Blade templates found']
    score = 0
    for root, _, files in os.walk(vdir):
        for f in files:
            if f.endswith('.blade.php'):
                score += 2
    score = min(score, RUBRIC['Views'])
    return score, [f'{score/2} Blade templates found']

def check_readme(base):
    path = os.path.join(base, 'README.md')
    if not os.path.exists(path): return 0, ['README.md missing']
    content = read_file(path)
    score = 0
    if 'overlap' in content: score += 3
    if 'capacity' in content: score += 3
    if 'reflection' in content: score += 2
    if 'screenshot' in content: score += 2
    return min(score, RUBRIC['Documentation']), ['README reviewed']

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

def generate_html_report(repo_name, results, total_score, local_path):
    """Generate HTML report for Laravel grading"""
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
        else:
            score = details.get('score', 0)
            max_score = RUBRIC.get(category, 0)
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

# --- MAIN ---

def grade_project(repo, path):
    results = {}
    total = 0
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

    ai = ai_feedback(path)
    results['AI Review'] = ai

    return min(total, 100), results

# --- EXECUTION ---

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    repos = [r for r in org.get_repos() if r.name.startswith(ASSIGNMENT_REPO_PREFIX)]
    
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
            print(f"[EXISTS] Repository already cloned, pulling latest changes...")
            try:
                r = Repo(local_path)
                r.remotes.origin.pull()
            except Exception as e:
                print(f"[WARNING] Could not pull latest changes: {e}")
        
        # Grade the project
        try:
            r = Repo(local_path)
            score, results = grade_project(r, local_path)
            
            print(f'\n[RESULT] Final Score: {score}/100')
            
            # Save JSON report
            json_path = os.path.join(local_path, 'grading_result.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f'[SAVED] JSON report: {json_path}')
            
            # Generate HTML report
            html_report = generate_html_report(repo.name, results, score, local_path)
            print(f'[SAVED] HTML report: {html_report}')
            
        except Exception as e:
            print(f"[ERROR] Failed to grade project: {e}")
            continue
    
    print(f'\n{"="*70}')
    print("Grading complete!")
    print("="*70)

if __name__ == '__main__':
    main()
