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
from datetime import datetime

def display_menu():
    """Display the main grading system menu"""
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
    
def grade_atm_project():
    """Run the ATM Banking System grader"""
    print("\n[LOADING] ATM Banking System Grader...")
    try:
        import Main
        Main.main()
    except ImportError as e:
        print(f"Error: Could not load Main.py: {e}")
    except Exception as e:
        print(f"Error during ATM grading: {e}")

def grade_laravel_project():
    """Run the Laravel Event Management grader"""
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

def main():
    """Main entry point for the unified grading system"""
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            grade_atm_project()
        elif choice == "2":
            grade_laravel_project()
        elif choice == "3":
            view_reports()
        elif choice == "4":
            compare_performance()
        elif choice == "5":
            print("\n[EXIT] Thank you for using the Unified Grading System!")
            print("Goodbye!\n")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 5.")
        
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
