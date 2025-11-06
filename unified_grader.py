"""
Unified Grading System
Supports both ATM Banking System and Laravel Event Management projects

Configuration:
- ATM Banking System uses ATM_* variables in config.py
- Laravel Event Management uses LARAVEL_* variables in config.py
- Run 'python show_config.py' to view all configuration values
"""

import sys
import os
import json
import io
import subprocess
from datetime import datetime

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class UnifiedGradingMenu:
    """Unified menu system for both ATM and Laravel grading"""
    
    def __init__(self):
        self.clear_screen()
        self.show_banner()
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_banner(self):
        """Display the welcome banner"""
        print("=" * 80)
        print("🎓  UNIFIED AUTO-GRADING SYSTEM  🎓".center(80))
        print("=" * 80)
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
        print("=" * 80)
        print()
    
    def show_main_menu(self):
        """Display the main project selection menu"""
        print("\n" + "─" * 80)
        print("MAIN MENU - SELECT PROJECT TYPE".center(80))
        print("─" * 80)
        print()
        print("  [1] ATM Banking System (PHP) - Milestone-based grading")
        print("  [2] Laravel Event Management - Rubric-based grading")
        print("  [3] View Grading Reports")
        print("  [4] Compare Student Performance")
        print("  [5] View Configuration")
        print("  [6] Exit")
        print()
        print("─" * 80)
    
    def show_atm_menu(self):
        """Display ATM Banking System sub-menu"""
        print("\n" + "─" * 80)
        print("ATM BANKING SYSTEM MENU".center(80))
        print("─" * 80)
        print()
        print("  [1] Grade All Students")
        print("  [2] Upload Grades to Moodle")
        print("  [3] Send Teams Messages")
        print("  [4] Verify Email Mappings")
        print("  [5] View Student Summary")
        print("  [6] Back to Main Menu")
        print()
        print("─" * 80)
    
    def show_laravel_menu(self):
        """Display Laravel Event Management sub-menu"""
        print("\n" + "─" * 80)
        print("LARAVEL EVENT MANAGEMENT MENU".center(80))
        print("─" * 80)
        print()
        print("  [1] Grade All Students (use existing repos)")
        print("  [2] Grade All Students (pull latest changes)")
        print("  [3] Grade Specific Students (selective grading)")
        print("  [4] Upload Grades to Moodle")
        print("  [5] Send Teams Notifications")
        print("  [6] View Student Summary")
        print("  [7] Back to Main Menu")
        print()
        print("─" * 80)
    
    def pause(self):
        """Pause and wait for user input"""
        print()
        input("Press Enter to continue...")
    
    def run_script(self, script_name, args=None, description="Running script"):
        """Run a Python script and show output in real-time"""
        print("\n" + "=" * 80)
        print(f"▶  {description}".center(80))
        print("=" * 80)
        print()
        
        try:
            # Build command
            cmd = [sys.executable, script_name]
            if args:
                cmd.extend(args)
            
            # Run the script with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            # Print output in real-time
            for line in process.stdout:
                print(line, end='', flush=True)
            
            process.wait()
            
            print()
            if process.returncode == 0:
                print("✅ Operation completed successfully!")
            else:
                print(f"⚠️ Operation completed with exit code: {process.returncode}")
        
        except FileNotFoundError:
            print(f"❌ Error: {script_name} not found!")
        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
        
        print()
        print("=" * 80)

def display_menu():
    """Legacy function - kept for compatibility"""
    print("\n" + "=" * 70)
    print("UNIFIED AUTO-GRADING SYSTEM")
    print("=" * 70)
    print("\nSelect Project Type to Grade:")
    print("\n1. ATM Banking System (PHP) - Milestone-based grading")
    print("2. Laravel Event Management - Rubric-based grading")
    print("3. View Grading Reports")
    print("4. Compare Student Performance")
    print("5. Exit")
    print("\n" + "=" * 70)
    
def handle_atm_menu(menu):
    """Handle ATM Banking System sub-menu"""
    while True:
        menu.show_atm_menu()
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            # Grade all students
            print("\n⚠️ This will grade all ATM Banking System repositories.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                menu.run_script("Main.py", description="GRADING ALL ATM STUDENTS")
            else:
                print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '2':
            # Upload grades to Moodle
            summary_file = os.path.join("cloned_repos", "student_summary.txt")
            if not os.path.exists(summary_file):
                print("\n❌ Error: No grading results found!")
                print("   Please run grading first (Option 1).")
            else:
                print("\n⚠️ This will upload ATM student grades to Moodle.")
                print("   Make sure you have:")
                print("   - Configured Moodle credentials in config.py")
                print("   - Reviewed the grades in student_summary.txt")
                confirm = input("\nContinue? (y/n): ").strip().lower()
                if confirm == 'y':
                    menu.run_script("MoodleIntegration.py", description="UPLOADING ATM GRADES TO MOODLE")
                else:
                    print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '3':
            # Send Teams messages
            if not os.path.exists("cloned_repos"):
                print("\n❌ Error: No grading results found!")
                print("   Please run grading first.")
            else:
                print("\n⚠️ This will send ATM grade reports to all students via Microsoft Teams.")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm == 'y':
                    menu.run_script("chatMessage.py", description="SENDING TEAMS MESSAGES")
                else:
                    print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '4':
            # Verify email mappings
            menu.run_script("verify_mappings.py", description="VERIFYING EMAIL MAPPINGS")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '5':
            # View student summary
            view_atm_summary()
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '6':
            # Back to main menu
            menu.clear_screen()
            menu.show_banner()
            break
        
        else:
            print(f"\n❌ Invalid option: {choice}")
            print("   Please select a number between 1 and 6.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()

def handle_laravel_menu(menu):
    """Handle Laravel Event Management sub-menu"""
    while True:
        menu.show_laravel_menu()
        choice = input("Select an option (1-7): ").strip()
        
        if choice == '1':
            # Grade all students (use existing repos)
            print("\n⚠️ This will grade all Laravel Event Management repositories.")
            print("   Using existing cloned repositories (no pull).")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                menu.run_script("Laravel_grader.py", description="GRADING ALL LARAVEL STUDENTS")
            else:
                print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '2':
            # Grade all students (pull latest changes)
            print("\n⚠️ This will grade all Laravel Event Management repositories.")
            print("   Pulling latest changes from GitHub before grading.")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                menu.run_script("Laravel_grader.py", args=["--update"], description="GRADING ALL LARAVEL STUDENTS (WITH UPDATE)")
            else:
                print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '3':
            # Grade specific students (selective grading)
            print("\n📋 SELECTIVE GRADING")
            print("=" * 70)
            print("Enter GitHub usernames (without repo prefix) separated by spaces.")
            print("Example: ndrewpk p-e-koko glad1223")
            print()
            students = input("Students to grade: ").strip()
            
            if not students:
                print("❌ No students specified. Operation cancelled.")
                menu.pause()
                menu.clear_screen()
                menu.show_banner()
                continue
            
            # Options
            print("\n⚙️ OPTIONS:")
            pull = input("Pull latest changes? (y/n): ").strip().lower() == 'y'
            skip_teams = input("Skip Teams notifications? (y/n): ").strip().lower() == 'y'
            skip_moodle = input("Skip Moodle upload? (y/n): ").strip().lower() == 'y'
            
            # Build command
            args = ["--students"] + students.split()
            if pull:
                args.append("--update")
            if skip_teams:
                args.append("--skip-teams")
            if skip_moodle:
                args.append("--skip-moodle")
            
            # Confirm
            print(f"\n📊 Summary:")
            print(f"   Students: {students}")
            print(f"   Pull changes: {'Yes' if pull else 'No'}")
            print(f"   Send Teams: {'No' if skip_teams else 'Yes'}")
            print(f"   Upload Moodle: {'No' if skip_moodle else 'Yes'}")
            confirm = input("\nContinue? (y/n): ").strip().lower()
            
            if confirm == 'y':
                menu.run_script("Laravel_grader.py", args=args, description="SELECTIVE GRADING")
            else:
                print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '4':
            # Upload grades to Moodle
            if not os.path.exists("cloned_repos"):
                print("\n❌ Error: No grading results found!")
                print("   Please run grading first (Option 1, 2, or 3).")
            else:
                print("\n⚠️ This will upload Laravel student grades to Moodle.")
                print("   Make sure you have:")
                print("   - Configured LARAVEL_MOODLE_* settings in config.py")
                print("   - Reviewed the grades in result.html files")
                confirm = input("\nContinue? (y/n): ").strip().lower()
                if confirm == 'y':
                    upload_laravel_grades_to_moodle()
                else:
                    print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '5':
            # Send Teams notifications
            if not os.path.exists("cloned_repos"):
                print("\n❌ Error: No grading results found!")
                print("   Please run grading first.")
            else:
                print("\n⚠️ This will send Laravel grade notifications to all students via Microsoft Teams.")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm == 'y':
                    send_laravel_teams_notifications()
                else:
                    print("Operation cancelled.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '6':
            # View student summary
            view_laravel_summary()
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '7':
            # Back to main menu
            menu.clear_screen()
            menu.show_banner()
            break
        
        else:
            print(f"\n❌ Invalid option: {choice}")
            print("   Please select a number between 1 and 7.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()

def grade_atm_project():
    """Legacy function - Run the ATM Banking System grader"""
    print("\n[LOADING] ATM Banking System Grader...")
    try:
        import Main
        Main.main()
    except ImportError as e:
        print(f"Error: Could not load Main.py: {e}")
    except Exception as e:
        print(f"Error during ATM grading: {e}")

def grade_laravel_project():
    """Legacy function - Run the Laravel Event Management grader"""
    print("\n[LOADING] Laravel Event Management Grader...")
    try:
        import Laravel_grader
        Laravel_grader.main()
    except ImportError as e:
        print(f"Error: Could not load Laravel_grader.py: {e}")
    except Exception as e:
        print(f"Error during Laravel grading: {e}")

def view_reports():
    """View existing grading reports"""
    print("\n" + "=" * 70)
    print("VIEW GRADING REPORTS")
    print("=" * 70)
    
    print("\n1. View ATM Project Reports")
    print("2. View Laravel Project Reports")
    print("3. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        view_atm_reports()
    elif choice == "2":
        view_laravel_reports()
    elif choice == "3":
        return
    else:
        print("Invalid choice. Please try again.")
        view_reports()

def view_atm_summary():
    """View ATM student summary"""
    import re
    
    output_dir = "cloned_repos"
    
    if not os.path.exists(output_dir):
        print("\n❌ Error: No grading results found!")
        print("   Please run grading first.")
        return
    
    print("\n" + "=" * 80)
    print("ATM BANKING SYSTEM - STUDENT SUMMARY".center(80))
    print("=" * 80)
    print()
    
    try:
        # Read grades from individual result files
        students = []
        
        for repo_name in os.listdir(output_dir):
            repo_path = os.path.join(output_dir, repo_name)
            
            # Skip if not a directory or not an ATM repo
            if not os.path.isdir(repo_path) or not repo_name.startswith("midterm-exam-atm-"):
                continue
            
            # Look for result files
            result_file = os.path.join(repo_path, "result.txt")
            if not os.path.exists(result_file):
                result_file = os.path.join(repo_path, "result.html")
            
            if not os.path.exists(result_file):
                continue
            
            # Read and parse the result file
            try:
                with open(result_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Extract information
                github_username = "Unknown"
                username_match = re.search(r'GitHub Username:\s*@?([^\s\n<]+)', content)
                if username_match:
                    github_username = username_match.group(1)
                
                final_score = 0.0
                score_match = re.search(r'FINAL TOTAL SCORE:\s*([\d.]+)/100', content)
                if not score_match:
                    score_match = re.search(r'Final Score:\s*([\d.]+)\s*/\s*100', content)
                if score_match:
                    final_score = float(score_match.group(1))
                
                grade = "N/A"
                grade_match = re.search(r'FINAL GRADE:\s*([^<\n]+)', content)
                if not grade_match:
                    grade_match = re.search(r'Grade:\s*([^\n<]+)', content)
                if grade_match:
                    grade = grade_match.group(1).strip()
                
                students.append({
                    'repo_name': repo_name,
                    'github_username': github_username,
                    'final_score': final_score,
                    'grade': grade
                })
            
            except Exception as e:
                print(f"Error reading {repo_name}: {e}")
                continue
        
        # Display summary
        if not students:
            print("No graded ATM students found.")
        else:
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            print()
            
            for student in students:
                print(f"Repository: {student['repo_name']}")
                print(f"GitHub Username: @{student['github_username']}")
                print(f"Final Score: {student['final_score']:.2f}/100")
                print(f"Grade: {student['grade']}")
                print("-" * 80)
                print()
            
            print(f"Total students: {len(students)}")
    
    except Exception as e:
        print(f"Error reading summary: {e}")
    
    print("=" * 80)

def view_laravel_summary():
    """View Laravel student summary"""
    import re
    
    output_dir = "cloned_repos"
    
    if not os.path.exists(output_dir):
        print("\n❌ Error: No grading results found!")
        print("   Please run grading first.")
        return
    
    print("\n" + "=" * 80)
    print("LARAVEL EVENT MANAGEMENT - STUDENT SUMMARY".center(80))
    print("=" * 80)
    print()
    
    try:
        students = []
        
        for repo_name in os.listdir(output_dir):
            repo_path = os.path.join(output_dir, repo_name)
            
            # Skip if not a directory or not a Laravel repo
            if not os.path.isdir(repo_path) or not repo_name.startswith("event-scheduler-"):
                continue
            
            # Look for grading_result.json in the repo or subdirectories
            json_found = False
            for root, dirs, files in os.walk(repo_path):
                if "grading_result.json" in files:
                    json_path = os.path.join(root, "grading_result.json")
                    html_path = os.path.join(root, "result.html")
                    
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Calculate total score
                        total_score = 0
                        for category, details in data.items():
                            if category != "AI Review" and isinstance(details, dict):
                                total_score += details.get('score', 0)
                        
                        # Determine grade
                        if total_score >= 80:
                            grade = "A (Excellent)"
                        elif total_score >= 75:
                            grade = "B+ (Very Good)"
                        elif total_score >= 70:
                            grade = "B (Good)"
                        elif total_score >= 65:
                            grade = "C+ (Satisfactory)"
                        elif total_score >= 60:
                            grade = "C (Passing)"
                        else:
                            grade = "F (Failing)"
                        
                        # Extract student username from repo name
                        student_username = repo_name.replace("event-scheduler-", "")
                        
                        students.append({
                            'repo_name': repo_name,
                            'github_username': student_username,
                            'final_score': total_score,
                            'grade': grade,
                            'html_report': html_path if os.path.exists(html_path) else None
                        })
                        
                        json_found = True
                        break
                    
                    except Exception as e:
                        print(f"Error reading {repo_name}: {e}")
                        continue
            
            if not json_found:
                print(f"⚠️  No grading results found for {repo_name}")
        
        # Display summary
        if not students:
            print("No graded Laravel students found.")
        else:
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            print()
            
            for student in students:
                print(f"Repository: {student['repo_name']}")
                print(f"GitHub Username: @{student['github_username']}")
                print(f"Final Score: {student['final_score']:.2f}/100")
                print(f"Grade: {student['grade']}")
                if student['html_report']:
                    print(f"Report: {student['html_report']}")
                print("-" * 80)
                print()
            
            print(f"Total students: {len(students)}")
    
    except Exception as e:
        print(f"Error reading summary: {e}")
    
    print("=" * 80)

def upload_laravel_grades_to_moodle():
    """Upload Laravel grades to Moodle using MoodleIntegration.py functions"""
    print("\n" + "=" * 80)
    print("▶  UPLOADING LARAVEL GRADES TO MOODLE".center(80))
    print("=" * 80)
    print()
    
    try:
        # Import from MoodleIntegration module
        import MoodleIntegration
        
        from config import (
            MOODLE_URL, MOODLE_TOKEN,
            LARAVEL_MOODLE_COURSE_ID,
            LARAVEL_MOODLE_ACTIVITY_ID,
            LARAVEL_MOODLE_GRADE_ITEM_ID,
            STUDENT_EMAILS
        )
        
        if not MOODLE_URL or not MOODLE_TOKEN:
            print("❌ Error: Moodle credentials not configured in config.py")
            return
        
        output_dir = "cloned_repos"
        
        # Collect Laravel grades
        print("[1/4] Collecting Laravel grades from result files...")
        laravel_grades = {}
        
        for repo_name in os.listdir(output_dir):
            repo_path = os.path.join(output_dir, repo_name)
            
            if not os.path.isdir(repo_path) or not repo_name.startswith("event-scheduler-"):
                continue
            
            # Find grading_result.json
            for root, dirs, files in os.walk(repo_path):
                if "grading_result.json" in files:
                    json_path = os.path.join(root, "grading_result.json")
                    
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Calculate total score
                        total_score = 0
                        for category, details in data.items():
                            if category != "AI Review" and isinstance(details, dict):
                                total_score += details.get('score', 0)
                        
                        # Extract student username
                        student_username = repo_name.replace("event-scheduler-", "")
                        
                        laravel_grades[repo_name] = {
                            'github_username': student_username,
                            'final_score': total_score,
                            'grade': 'N/A'  # We don't need grade letter for Moodle
                        }
                        
                        print(f"  ✓ {student_username}: {total_score}/100")
                        
                        break
                    
                    except Exception as e:
                        print(f"  ⚠️  Error processing {repo_name}: {e}")
                        continue
        
        if not laravel_grades:
            print("\n❌ No Laravel grades found. Please run grading first.")
            return
        
        print(f"\n  Found {len(laravel_grades)} Laravel grade(s)")
        
        # Test Moodle connection
        print("\n[2/4] Testing Moodle connection...")
        result = MoodleIntegration.call_moodle_api('core_webservice_get_site_info')
        if not result:
            print("❌ Failed to connect to Moodle. Check your credentials.")
            return
        print(f"  ✅ Connected to {result.get('sitename', 'Moodle')}")
        
        # Get enrolled users
        print("\n[3/4] Retrieving enrolled users from Moodle...")
        
        # Get usernames from STUDENT_EMAILS for Laravel repos
        laravel_usernames = []
        username_to_repo = {}
        
        for repo_name, email in STUDENT_EMAILS.items():
            if repo_name.startswith("event-scheduler-"):
                moodle_username = email.split('@')[0]  # Extract username from email
                laravel_usernames.append(moodle_username)
                username_to_repo[moodle_username] = repo_name
        
        # Get users from Moodle
        all_users = []
        found_count = 0
        
        for username in laravel_usernames:
            result = MoodleIntegration.call_moodle_api('core_user_get_users', {
                'criteria[0][key]': 'username',
                'criteria[0][value]': username
            })
            
            if result and 'users' in result and len(result['users']) > 0:
                user = result['users'][0]
                all_users.append({
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'repo_name': username_to_repo.get(username)
                })
                found_count += 1
                print(f"  ✓ Found: {username} (ID: {user.get('id')})")
            else:
                print(f"  ✗ Not found: {username}")
        
        if not all_users:
            print("\n❌ No matching users found in Moodle.")
            return
        
        print(f"\n  Found {found_count}/{len(laravel_usernames)} user(s) in Moodle")
        
        # Update grades
        print("\n[4/4] Uploading grades to Moodle...")
        print(f"  Course ID: {LARAVEL_MOODLE_COURSE_ID}")
        print(f"  Activity ID: {LARAVEL_MOODLE_ACTIVITY_ID}")
        print(f"  Grade Item ID: {LARAVEL_MOODLE_GRADE_ITEM_ID}")
        print()
        
        success_count = 0
        failed_count = 0
        
        for user_info in all_users:
            user_id = user_info['id']
            username = user_info['username']
            repo_name = user_info['repo_name']
            
            # Get grade for this repo
            grade_info = laravel_grades.get(repo_name)
            if not grade_info:
                print(f"  ⚠️  {username}: No grade data found")
                continue
            
            final_score = grade_info['final_score']
            
            # Upload to Moodle using core_grades_update_grades
            result = MoodleIntegration.call_moodle_api('core_grades_update_grades', {
                'source': 'mod/assign',
                'courseid': LARAVEL_MOODLE_COURSE_ID,
                'component': 'mod_assign',
                'activityid': LARAVEL_MOODLE_ACTIVITY_ID,
                'itemnumber': 0,
                'grades[0][studentid]': user_id,
                'grades[0][grade]': final_score
            })
            
            if result is not None:
                print(f"  ✅ {username}: {final_score}/100 uploaded successfully")
                success_count += 1
            else:
                print(f"  ❌ {username}: Failed to upload grade")
                failed_count += 1
        
        # Save results
        print("\n" + "=" * 80)
        print(f"✅ Upload complete!")
        print(f"   Successfully uploaded: {success_count}/{len(all_users)}")
        print(f"   Failed: {failed_count}/{len(all_users)}")
        print("=" * 80)
        
        # Save results to file
        try:
            results_file = os.path.join(output_dir, "moodle_laravel_update_results.txt")
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("MOODLE LARAVEL GRADE UPDATE RESULTS\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Total students: {len(all_users)}\n")
                f.write(f"Successfully uploaded: {success_count}\n")
                f.write(f"Failed: {failed_count}\n\n")
                f.write("=" * 80 + "\n")
                f.write("DETAILS\n")
                f.write("=" * 80 + "\n\n")
                
                for user_info in all_users:
                    repo_name = user_info['repo_name']
                    grade_info = laravel_grades.get(repo_name, {})
                    f.write(f"Repository: {repo_name}\n")
                    f.write(f"Moodle Username: {user_info['username']}\n")
                    f.write(f"Grade: {grade_info.get('final_score', 0)}/100\n")
                    f.write("-" * 80 + "\n\n")
            
            print(f"\n✅ Results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save results to file: {e}")
    
    except ImportError as e:
        print(f"❌ Error: Could not import required modules: {e}")
        print("   Make sure MoodleIntegration.py exists in the project directory.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def send_laravel_teams_notifications():
    """Send Laravel grade notifications via Teams direct messages (using chatMessage.py approach)"""
    print("\n" + "=" * 80)
    print("▶  SENDING LARAVEL TEAMS NOTIFICATIONS".center(80))
    print("=" * 80)
    print()
    
    try:
        import requests
        import msal
        import time
        import logging
        
        # Import configuration
        try:
            from config import (
                TENANT_ID,
                CLIENT_ID,
                CLIENT_SECRET,
                INSTRUCTOR_EMAIL,
                STUDENT_EMAILS,
                LARAVEL_ASSIGNMENT_REPO_PREFIX
            )
        except ImportError as e:
            print(f"❌ Error: Missing configuration in config.py: {e}")
            print("   Please ensure TENANT_ID, CLIENT_ID, INSTRUCTOR_EMAIL are configured.")
            return
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        
        AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
        SCOPES = ["User.Read", "Chat.ReadWrite"]
        GRAPH_URL = "https://graph.microsoft.com/v1.0"
        
        # Get access token
        print("[AUTH] Acquiring access token...")
        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if not result:
            print("[AUTH] Please sign in to your Microsoft account...")
            result = app.acquire_token_interactive(scopes=SCOPES)
        
        if "access_token" not in result:
            print(f"❌ Failed to acquire access token: {result.get('error_description')}")
            return
        
        token = result["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Access token acquired successfully")
        print()
        
        output_dir = "cloned_repos"
        sent_count = 0
        total_students = 0
        
        # Count total students to process
        for repo_name in os.listdir(output_dir):
            if repo_name.startswith("event-scheduler-"):
                total_students += 1
        
        print(f"Found {total_students} Laravel repositories to process")
        print("=" * 80)
        print()
        
        for repo_name in os.listdir(output_dir):
            repo_path = os.path.join(output_dir, repo_name)
            
            if not os.path.isdir(repo_path) or not repo_name.startswith("event-scheduler-"):
                continue
            
            # Extract student username from repo name
            student_username = repo_name.replace("event-scheduler-", "")
            
            # Find student email
            student_email = STUDENT_EMAILS.get(repo_name)
            if not student_email:
                print(f"⚠️  [{student_username}] No email mapping found in STUDENT_EMAILS, skipping...")
                continue
            
            print(f"[{sent_count + 1}/{total_students}] Processing {student_username} ({student_email})...")
            
            # Find result.html
            html_path = None
            for root, dirs, files in os.walk(repo_path):
                if "result.html" in files:
                    html_path = os.path.join(root, "result.html")
                    break
            
            if not html_path or not os.path.exists(html_path):
                print(f"  ⚠️  No result.html found, skipping...")
                continue
            
            try:
                # Read the HTML report
                with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
                    grade_content = f.read().strip()
                
                if not grade_content:
                    print(f"  ⚠️  Empty grade file, skipping...")
                    continue
                
                # Extract body content from HTML
                import re
                body_match = re.search(r'<body>(.*?)</body>', grade_content, re.DOTALL)
                if body_match:
                    grade_body = body_match.group(1).strip()
                else:
                    grade_body = grade_content.strip()
                
                # Compress HTML (remove excessive whitespace)
                grade_body = re.sub(r'\n\s+', '\n', grade_body)
                grade_body = re.sub(r'\s+', ' ', grade_body)
                grade_body = re.sub(r'>\s+<', '><', grade_body)
                
                # Build Teams-friendly message
                message_html = f"""
                <div style="font-family:'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size:13px; line-height:1.5; color:#2b2b2b; max-width:100%; overflow-x:hidden;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:20px; border-radius:12px; margin-bottom:25px; text-align:center;">
                        <h1 style="margin:0; font-size:24px; font-weight:600;">Laravel Event Management Project</h1>
                        <h2 style="margin:5px 0 0 0; font-size:18px; font-weight:400; opacity:0.9;">Grade Report</h2>
                        <p style="margin:8px 0 0; font-size:14px; opacity:0.8;">Muaklek Campus</p>
                    </div>

                    <div style="background:#ffffff; padding:25px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.1); margin-bottom:20px;">
                        <p style="margin:0 0 15px 0; font-size:16px;"><strong>Hello {student_username},</strong></p>
                        <p style="margin:0; color:#666; font-size:14px;">Please find your detailed Laravel project grade report below.</p>
                    </div>

                    <div style="background:#ffffff; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.1); overflow:hidden;">
                        <div style="padding:25px; max-height:none; overflow-y:visible;">
                            {grade_body}
                        </div>
                    </div>

                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:20px; border-radius:12px; margin-top:25px; text-align:center;">
                        <p style="margin:0 0 10px 0; font-size:16px; font-weight:600;">Best regards,</p>
                        <p style="margin:0 0 15px 0; font-size:14px;">Mr. Rindra</p>
                        <p style="margin:0; font-size:12px; opacity:0.8;">Sent automatically via Microsoft Teams</p>
                    </div>
                </div>
                """
                
                # Create or get existing chat
                chat_payload = {
                    "chatType": "oneOnOne",
                    "members": [
                        {
                            "@odata.type": "#microsoft.graph.aadUserConversationMember",
                            "roles": ["owner"],
                            "user@odata.bind": f"{GRAPH_URL}/users('{INSTRUCTOR_EMAIL}')"
                        },
                        {
                            "@odata.type": "#microsoft.graph.aadUserConversationMember",
                            "roles": ["owner"],
                            "user@odata.bind": f"{GRAPH_URL}/users('{student_email}')"
                        }
                    ]
                }
                
                chat_resp = requests.post(f"{GRAPH_URL}/chats", headers=headers, json=chat_payload)
                if chat_resp.status_code not in [200, 201]:
                    print(f"  ❌ Failed to create chat: {chat_resp.text}")
                    continue
                
                chat_id = chat_resp.json()["id"]
                
                # Send message
                msg_payload = {
                    "body": {
                        "contentType": "html",
                        "content": message_html
                    }
                }
                
                msg_resp = requests.post(f"{GRAPH_URL}/chats/{chat_id}/messages", headers=headers, json=msg_payload)
                
                if msg_resp.status_code in [200, 201]:
                    print(f"  ✅ Message sent successfully")
                    sent_count += 1
                else:
                    print(f"  ❌ Failed to send message: {msg_resp.status_code} - {msg_resp.text}")
                
                # Add delay to avoid rate limiting
                time.sleep(2)
            
            except Exception as e:
                print(f"  ❌ Error processing {student_username}: {e}")
                continue
        
        print()
        print(f"{'=' * 80}")
        print(f"✅ Notification complete! Sent {sent_count}/{total_students} messages to Teams.")
        print(f"{'=' * 80}")
    
    except ImportError as e:
        print(f"❌ Error: Missing required module: {e}")
        print("   Please install: pip install msal requests")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def view_atm_reports():
    """View ATM Banking System reports"""
    from config import OUTPUT_DIR
    
    print("\n[SEARCHING] ATM Project Reports in:", OUTPUT_DIR)
    
    if not os.path.exists(OUTPUT_DIR):
        print("No reports found. Please run grading first.")
        return
    
    # Find all result.html files
    reports = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        if "result.html" in files:
            reports.append(os.path.join(root, "result.html"))
    
    if not reports:
        print("No ATM project reports found.")
        return
    
    print(f"\nFound {len(reports)} report(s):")
    for i, report in enumerate(reports, 1):
        folder = os.path.basename(os.path.dirname(report))
        print(f"{i}. {folder}")
    
    print(f"\n{len(reports) + 1}. Back to Reports Menu")
    
    choice = input(f"\nSelect report to open (1-{len(reports) + 1}): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(reports):
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(reports[idx])}")
            print(f"[OPENED] {reports[idx]}")
        elif idx == len(reports):
            return
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")

def view_laravel_reports():
    """View Laravel Event Management reports"""
    from config import OUTPUT_DIR
    
    print("\n[SEARCHING] Laravel Project Reports in:", OUTPUT_DIR)
    
    if not os.path.exists(OUTPUT_DIR):
        print("No reports found. Please run grading first.")
        return
    
    # Find all grading_result.json files
    reports = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        if "grading_result.json" in files:
            reports.append(os.path.join(root, "grading_result.json"))
    
    if not reports:
        print("No Laravel project reports found.")
        return
    
    print(f"\nFound {len(reports)} report(s):")
    for i, report in enumerate(reports, 1):
        folder = os.path.basename(os.path.dirname(report))
        print(f"{i}. {folder}")
    
    print(f"\n{len(reports) + 1}. Back to Reports Menu")
    
    choice = input(f"\nSelect report to view (1-{len(reports) + 1}): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(reports):
            import json
            with open(reports[idx], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n{'=' * 70}")
            print(f"LARAVEL PROJECT REPORT")
            print(f"{'=' * 70}")
            
            total_score = 0
            for category, details in data.items():
                if category == "AI Review":
                    print(f"\n{category}:")
                    print(f"  Summary: {details.get('summary', 'N/A')}")
                    suggestions = details.get('suggestions', [])
                    if isinstance(suggestions, list):
                        print(f"  Suggestions:")
                        for suggestion in suggestions:
                            print(f"    - {suggestion}")
                    else:
                        print(f"  Suggestions: {suggestions}")
                else:
                    score = details.get('score', 0)
                    total_score += score
                    print(f"\n{category}: {score} pts")
                    for remark in details.get('remarks', []):
                        print(f"  - {remark}")
            
            print(f"\n{'=' * 70}")
            print(f"TOTAL SCORE: {total_score}/100")
            print(f"{'=' * 70}")
            
            input("\nPress Enter to continue...")
        elif idx == len(reports):
            return
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error reading report: {e}")

def compare_performance():
    """Compare student performance across both project types"""
    from config import OUTPUT_DIR
    
    print("\n" + "=" * 70)
    print("STUDENT PERFORMANCE COMPARISON")
    print("=" * 70)
    
    # Read ATM summary
    atm_summary_path = os.path.join(OUTPUT_DIR, "student_summary.txt")
    atm_students = {}
    
    if os.path.exists(atm_summary_path):
        try:
            with open(atm_summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse student data (simplified)
                print("\n[ATM Banking System Grades]")
                print(content)
        except Exception as e:
            print(f"Error reading ATM summary: {e}")
    else:
        print("\n[ATM Banking System] No summary found.")
    
    # Read Laravel grades
    print("\n" + "=" * 70)
    print("[Laravel Event Management Grades]")
    print("=" * 70)
    laravel_found = False
    
    for root, dirs, files in os.walk(OUTPUT_DIR):
        if "grading_result.json" in files:
            repo_name = os.path.basename(root)
            json_path = os.path.join(root, "grading_result.json")
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_score = sum(d.get('score', 0) for k, d in data.items() if k != "AI Review")
                    print(f"\n{repo_name}: {total_score}/100")
                    laravel_found = True
            except Exception as e:
                print(f"Error reading {repo_name}: {e}")
    
    if not laravel_found:
        print("No Laravel project grades found.")
    
    input("\n\nPress Enter to continue...")

def view_configuration():
    """View current configuration"""
    print("\n" + "=" * 80)
    print("⚙  CURRENT CONFIGURATION".center(80))
    print("=" * 80)
    print()
    
    try:
        from config import (
            ORG_NAME,
            ASSIGNMENT_REPO_PREFIX,
            LARAVEL_ASSIGNMENT_REPO_PREFIX,
            SUBMISSION_DEADLINE,
            FREEZE_GRADING,
            MOODLE_URL,
            MOODLE_TOKEN
        )
        
        print("=" * 80)
        print("ATM BANKING SYSTEM CONFIGURATION")
        print("=" * 80)
        print(f"Organization: {ORG_NAME}")
        print(f"Repository Prefix: {ASSIGNMENT_REPO_PREFIX}")
        print(f"Submission Deadline: {SUBMISSION_DEADLINE}")
        print(f"Grading Status: {'🔒 Frozen' if FREEZE_GRADING else '🔓 Active'}")
        
        print()
        print("=" * 80)
        print("LARAVEL EVENT MANAGEMENT CONFIGURATION")
        print("=" * 80)
        print(f"Organization: {ORG_NAME}")
        print(f"Repository Prefix: {LARAVEL_ASSIGNMENT_REPO_PREFIX}")
        
        print()
        print("=" * 80)
        print("INTEGRATION CONFIGURATION")
        print("=" * 80)
        print(f"Moodle URL: {MOODLE_URL if MOODLE_URL else '❌ Not configured'}")
        print(f"Moodle Token: {'✅ Configured' if MOODLE_TOKEN else '❌ Not configured'}")
        
        webhook_url = os.environ.get('TEAMS_WEBHOOK_URL')
        print(f"Teams Webhook: {'✅ Configured' if webhook_url else '❌ Not configured'}")
    
    except Exception as e:
        print(f"Error loading configuration: {e}")
    
    print()
    print("=" * 80)

def main():
    """Main entry point for the unified grading system"""
    menu = UnifiedGradingMenu()
    
    while True:
        menu.show_main_menu()
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            # ATM Banking System
            menu.clear_screen()
            menu.show_banner()
            handle_atm_menu(menu)
        
        elif choice == '2':
            # Laravel Event Management
            menu.clear_screen()
            menu.show_banner()
            handle_laravel_menu(menu)
        
        elif choice == '3':
            # View Reports
            view_reports()
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '4':
            # Compare Performance
            compare_performance()
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '5':
            # View Configuration
            view_configuration()
            menu.pause()
            menu.clear_screen()
            menu.show_banner()
        
        elif choice == '6':
            # Exit
            print("\n" + "=" * 80)
            print("Thank you for using the Unified Grading System!".center(80))
            print("=" * 80)
            print()
            break
        
        else:
            print(f"\n❌ Invalid option: {choice}")
            print("   Please select a number between 1 and 6.")
            menu.pause()
            menu.clear_screen()
            menu.show_banner()

if __name__ == "__main__":
    main()
