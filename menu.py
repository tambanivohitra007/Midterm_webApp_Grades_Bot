"""
Student Grading System - Console Menu Interface
A simple, reliable console-based interface for managing the grading system
"""

import os
import sys
import subprocess
from datetime import datetime

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class GradingMenu:
    def __init__(self):
        self.clear_screen()
        self.show_banner()

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        """Display the welcome banner"""
        print("=" * 80)
        print("🎓  STUDENT GRADING SYSTEM MANAGER  🎓".center(80))
        print("=" * 80)
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
        print("=" * 80)
        print()

    def show_menu(self):
        """Display the main menu"""
        print("\n" + "─" * 80)
        print("MAIN MENU".center(80))
        print("─" * 80)
        print()
        print("  [1] Grade All Students")
        print("  [2] Upload Grades to Moodle")
        print("  [3] Send Teams Messages")
        print("  [4] Verify Email Mappings")
        print("  [5] View Student Summary")
        print("  [6] View Configuration")
        print("  [7] Refresh Status")
        print("  [8] Open Config File")
        print("  [9] Exit")
        print()
        print("─" * 80)

    def show_status(self):
        """Display system status"""
        try:
            from config import (
                ORG_NAME,
                ASSIGNMENT_REPO_PREFIX,
                SUBMISSION_DEADLINE,
                FREEZE_GRADING,
                STUDENT_EMAILS
            )

            print("\n" + "─" * 80)
            print("ℹ  SYSTEM STATUS".center(80))
            print("─" * 80)
            print(f"  Organization: {ORG_NAME}")
            print(f"  Repo Prefix: {ASSIGNMENT_REPO_PREFIX}")
            print(f"  Deadline: {SUBMISSION_DEADLINE}")
            print(f"  Grading Status: {'🔒 Frozen' if FREEZE_GRADING else '🔓 Active'}")
            print(f"  Students Mapped: {len(STUDENT_EMAILS)}")

            # Check graded count
            if os.path.exists("cloned_repos"):
                graded_count = len([
                    d for d in os.listdir("cloned_repos")
                    if os.path.isdir(os.path.join("cloned_repos", d))
                    and os.path.exists(os.path.join("cloned_repos", d, "result.txt"))
                ])
                print(f"  Students Graded: {graded_count}")
            else:
                print(f"  Students Graded: 0")

            # Check Moodle configuration
            try:
                from config import MOODLE_URL, MOODLE_TOKEN
                if MOODLE_URL and MOODLE_TOKEN:
                    print(f"  Moodle Integration: ✅ Configured")
                else:
                    print(f"  Moodle Integration: ⚠️  Not configured")
            except ImportError:
                print(f"  Moodle Integration: ⚠️  Not configured")

            print("─" * 80)

        except Exception as e:
            print(f"Error loading status: {e}")

    def run_script(self, script_name, description):
        """Run a Python script and show output in real-time"""
        print("\n" + "=" * 80)
        print(f"▶  {description}".center(80))
        print("=" * 80)
        print()

        try:
            # Run the script with real-time output
            process = subprocess.Popen(
                [sys.executable, script_name],
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
                print("peration completed successfully!")
            else:
                print(f"Operation failed with exit code: {process.returncode}")

        except FileNotFoundError:
            print(f"Error: {script_name} not found!")
        except Exception as e:
            print(f"Error running {script_name}: {e}")

        print()
        print("=" * 80)

    def grade_all_students(self):
        """Grade all student repositories"""
        print("\n⚠This will grade all student repositories.")
        confirm = input("Continue? (y/n): ").strip().lower()

        if confirm == 'y':
            self.run_script("Main.py", "GRADING ALL STUDENTS")
        else:
            print("Operation cancelled.")

    def upload_grades_to_moodle(self):
        """Upload grades to Moodle"""
        summary_file = os.path.join("cloned_repos", "student_summary.txt")

        if not os.path.exists(summary_file):
            print("\nError: No grading results found!")
            print("   Please run grading first (Option 1).")
            return

        print("\n⚠This will upload student grades to Moodle.")
        print("   Make sure you have:")
        print("   - Configured Moodle credentials in config.py")
        print("   - Reviewed the grades in student_summary.txt")
        print("   - Uncommented student emails in config.py STUDENT_EMAILS")
        confirm = input("\nContinue? (y/n): ").strip().lower()

        if confirm == 'y':
            self.run_script("MoodleIntegration.py", "UPLOADING GRADES TO MOODLE")
        else:
            print("Operation cancelled.")

    def send_teams_messages(self):
        """Send messages via Microsoft Teams"""
        if not os.path.exists("cloned_repos"):
            print("\nError: No grading results found!")
            print("   Please run grading first.")
            return

        print("\n⚠This will send grade reports to all students via Microsoft Teams.")
        confirm = input("Continue? (y/n): ").strip().lower()

        if confirm == 'y':
            self.run_script("chatMessage.py", "SENDING TEAMS MESSAGES")
        else:
            print("Operation cancelled.")

    def verify_mappings(self):
        """Verify email mappings"""
        self.run_script("verify_mappings.py", "VERIFYING EMAIL MAPPINGS")

    def view_summary(self):
        """View student summary - read from individual result files"""
        import re
        from datetime import datetime

        output_dir = "cloned_repos"

        if not os.path.exists(output_dir):
            print("\nError: No grading results found!")
            print("   Please run grading first.")
            return

        print("\n" + "=" * 80)
        print("STUDENT SUMMARY".center(80))
        print("=" * 80)
        print()

        try:
            # Read grades from individual result files
            students = []

            for repo_name in os.listdir(output_dir):
                repo_path = os.path.join(output_dir, repo_name)

                # Skip if not a directory
                if not os.path.isdir(repo_path):
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

                    # Extract information (handle both HTML and plain text)
                    github_username = "Unknown"
                    # Try HTML format first: <strong>GitHub Username:</strong> @username
                    username_match = re.search(r'<strong>GitHub Username:</strong>\s*@?([^\s<]+)', content)
                    if not username_match:
                        # Fallback to plain text: GitHub Username: @username
                        username_match = re.search(r'GitHub Username:\s*@?([^\s\n<]+)', content)
                    if username_match:
                        github_username = username_match.group(1)

                    final_score = 0.0
                    # Try HTML format: FINAL TOTAL SCORE: 88.76/100 pts
                    score_match = re.search(r'FINAL TOTAL SCORE:\s*([\d.]+)/100', content)
                    if not score_match:
                        # Fallback to plain text: Final Score: 88.76/100
                        score_match = re.search(r'Final Score:\s*([\d.]+)\s*/\s*100', content)
                    if score_match:
                        final_score = float(score_match.group(1))

                    grade = "N/A"
                    # Try HTML format: FINAL GRADE: A (Excellent)
                    grade_match = re.search(r'FINAL GRADE:\s*([^<\n]+)', content)
                    if not grade_match:
                        # Fallback to plain text: Grade: A (Excellent)
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
                print("No graded students found.")
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

    def view_configuration(self):
        """View current configuration"""
        print("\n" + "=" * 80)
        print("⚙  CURRENT CONFIGURATION".center(80))
        print("=" * 80)
        print()

        try:
            from config import (
                ORG_NAME,
                ASSIGNMENT_REPO_PREFIX,
                SUBMISSION_DEADLINE,
                FREEZE_GRADING,
                GRADE_COMMITS_UNTIL,
                INSTRUCTION_FOLLOWING_BONUS,
                INSTRUCTION_THRESHOLD,
                LATE_SUBMISSION_PENALTY,
                STUDENT_EMAILS
            )

            print(f"Organization: {ORG_NAME}")
            print(f"Repository Prefix: {ASSIGNMENT_REPO_PREFIX}")
            print(f"Submission Deadline: {SUBMISSION_DEADLINE}")
            print(f"Grading Status: {'🔒 Frozen' if FREEZE_GRADING else '🔓 Active'}")
            print(f"Grade Commits Until: {GRADE_COMMITS_UNTIL if GRADE_COMMITS_UNTIL else 'No cutoff'}")
            print(f"Instruction Following Bonus: +{INSTRUCTION_FOLLOWING_BONUS} points (threshold: {INSTRUCTION_THRESHOLD}%)")
            print(f"Late Submission Penalty: -{LATE_SUBMISSION_PENALTY} points")
            print(f"Students Mapped: {len(STUDENT_EMAILS)}")

        except Exception as e:
            print(f"Error loading configuration: {e}")

        print()
        print("=" * 80)

    def open_config_file(self):
        """Open the configuration file"""
        config_file = "config.py"

        if not os.path.exists(config_file):
            print("\nError: config.py not found!")
            return

        print(f"\nOpening {config_file}...")

        try:
            if sys.platform == "win32":
                os.startfile(config_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", config_file])
            else:
                subprocess.run(["xdg-open", config_file])

            print("Config file opened in default editor.")
            print("After editing, use option [6] to refresh status.")

        except Exception as e:
            print(f"Error opening config file: {e}")

    def pause(self):
        """Pause and wait for user input"""
        print()
        input("Press Enter to continue...")

    def run(self):
        """Main menu loop"""
        while True:
            self.show_status()
            self.show_menu()

            try:
                choice = input("Select an option (1-9): ").strip()

                if choice == '1':
                    self.grade_all_students()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '2':
                    self.upload_grades_to_moodle()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '3':
                    self.send_teams_messages()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '4':
                    self.verify_mappings()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '5':
                    self.view_summary()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '6':
                    self.view_configuration()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '7':
                    self.clear_screen()
                    self.show_banner()
                    print("\nStatus refreshed!")

                elif choice == '8':
                    self.open_config_file()
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

                elif choice == '9':
                    print("\n" + "=" * 80)
                    print("Thank you for using Student Grading System!".center(80))
                    print("=" * 80)
                    print()
                    break

                else:
                    print(f"\nInvalid option: {choice}")
                    print("   Please select a number between 1 and 9.")
                    self.pause()
                    self.clear_screen()
                    self.show_banner()

            except KeyboardInterrupt:
                print("\n\n" + "=" * 80)
                print("Goodbye!".center(80))
                print("=" * 80)
                print()
                break

            except Exception as e:
                print(f"\nUnexpected error: {e}")
                self.pause()
                self.clear_screen()
                self.show_banner()


def main():
    """Main entry point"""
    menu = GradingMenu()
    menu.run()


if __name__ == "__main__":
    main()
