"""
Moodle Web Services API Integration Test
This script tests the feasibility of accessing Moodle and updating student grades.

Before running:
1. Enable Web Services in Moodle (Site Administration → Server → Web Services)
2. Create a web service token with grade update permissions
3. Add your Moodle credentials to config.py
"""

import requests
import json
import sys
import os
import re

# ------------------------------
# CONFIGURATION
# ------------------------------
try:
    from config import (
        MOODLE_URL,           # https://lms.apiu.edu
        MOODLE_TOKEN,         # web service token
        MOODLE_COURSE_ID,     # Course ID where grades will be updated
        MOODLE_ACTIVITY_ID,   # Assignment/Activity module ID
        MOODLE_GRADE_ITEM_ID, # Grade item ID (for grade updates)
        STUDENT_EMAILS,       # Student email mappings
        OUTPUT_DIR            # Directory where grades are stored
    )
    # For backward compatibility
    MOODLE_ASSIGNMENT_ID = MOODLE_GRADE_ITEM_ID
except ImportError:
    print("=" * 70)
    print("ERROR: Moodle configuration not found in config.py!")
    print("=" * 70)
    print("\nPlease add the following variables to your config.py file:\n")
    print("# Moodle Web Services Configuration")
    print("MOODLE_URL = 'https://lms.apiu.edu'  # Your Moodle URL")
    print("MOODLE_TOKEN = 'your_web_service_token_here'  # Get from Moodle admin")
    print("MOODLE_COURSE_ID = 123  # Your course ID (find in course URL)")
    print("MOODLE_ACTIVITY_ID = 144160  # Assignment module ID (from mod/assign/view.php?id=XXXXX)")
    print("MOODLE_GRADE_ITEM_ID = 76001  # Grade item ID (run test script to find this)")
    print("\n" + "=" * 70)
    print("How to get The Web Service Token:")
    print("=" * 70)
    print("1. Login to Moodle as admin")
    print("2. Go to: Site Administration → Server → Web Services → Overview")
    print("3. Follow the setup steps to enable web services")
    print("4. Go to: Site Administration → Server → Web Services → Manage tokens")
    print("5. Create a new token for your user")
    print("6. Grant permissions for grade-related functions")
    print("=" * 70)
    sys.exit(1)


# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

def get_student_usernames_from_config():
    """
    Extract Moodle usernames from STUDENT_EMAILS in config.py

    Returns:
        List of dictionaries with repo_name, moodle_username, and email
    """
    students = []
    for repo_name, email in STUDENT_EMAILS.items():
        # Extract username from email (e.g., "202480016" from "202480016@my.apiu.edu")
        moodle_username = email.split('@')[0]
        students.append({
            'repo_name': repo_name,
            'moodle_username': moodle_username,
            'email': email
        })
    return students


def read_grades_from_individual_results():
    """
    Read final grades directly from individual student result files
    This is more robust than relying on student_summary.txt

    Returns:
        Dictionary mapping repo_name to grade information:
        {
            'repo_name': {
                'github_username': 'username',
                'final_score': 85.50,
                'grade': 'A (Excellent)'
            }
        }
    """
    if not os.path.exists(OUTPUT_DIR):
        print(f"[WARN] Warning: {OUTPUT_DIR} directory not found!")
        print("   Please run Main.py first to generate student grades.")
        return {}

    grades = {}

    try:
        # Scan all directories in OUTPUT_DIR
        for repo_name in os.listdir(OUTPUT_DIR):
            repo_path = os.path.join(OUTPUT_DIR, repo_name)

            # Skip if not a directory
            if not os.path.isdir(repo_path):
                continue

            # Look for result files (prefer .txt, fallback to .html)
            result_file = os.path.join(repo_path, "result.txt")
            if not os.path.exists(result_file):
                result_file = os.path.join(repo_path, "result.html")

            if not os.path.exists(result_file):
                print(f"[WARN] No result file found for {repo_name}, skipping")
                continue

            # Read and parse the result file
            try:
                with open(result_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Extract GitHub username (handle both HTML and plain text)
                github_username = "Unknown"
                # Try HTML format first: <strong>GitHub Username:</strong> @username
                username_match = re.search(r'<strong>GitHub Username:</strong>\s*@?([^\s<]+)', content)
                if not username_match:
                    # Fallback to plain text: GitHub Username: @username
                    username_match = re.search(r'GitHub Username:\s*@?([^\s\n<]+)', content)
                if username_match:
                    github_username = username_match.group(1)

                # Extract final score
                final_score = 0.0
                # Try HTML format: FINAL TOTAL SCORE: 88.76/100 pts
                score_match = re.search(r'FINAL TOTAL SCORE:\s*([\d.]+)/100', content)
                if not score_match:
                    # Fallback to plain text: Final Score: 88.76/100
                    score_match = re.search(r'Final Score:\s*([\d.]+)\s*/\s*100', content)
                if score_match:
                    final_score = float(score_match.group(1))

                # Extract grade letter
                grade = "N/A"
                # Try HTML format: FINAL GRADE: A (Excellent)
                grade_match = re.search(r'FINAL GRADE:\s*([^<\n]+)', content)
                if not grade_match:
                    # Fallback to plain text: Grade: A (Excellent)
                    grade_match = re.search(r'Grade:\s*([^\n<]+)', content)
                if grade_match:
                    grade = grade_match.group(1).strip()

                # Store the grade information
                grades[repo_name] = {
                    'github_username': github_username,
                    'final_score': final_score,
                    'grade': grade
                }

            except Exception as e:
                print(f"[WARN] Error reading {result_file}: {e}")
                continue

        return grades

    except Exception as e:
        print(f"[FAIL] Error scanning grade directories: {e}")
        return {}


def map_github_to_moodle_users(students_config, grades_data):
    """
    Map GitHub usernames to Moodle usernames and include grade data

    Args:
        students_config: List from get_student_usernames_from_config()
        grades_data: Dictionary from read_grades_from_summary()

    Returns:
        List of dictionaries with complete student information:
        {
            'repo_name': 'midterm-exam-atm-username',
            'moodle_username': '202480016',
            'github_username': 'p-e-koko',
            'email': '202480016@my.apiu.edu',
            'final_score': 88.76,
            'grade': 'A (Excellent)'
        }
    """
    mapped_students = []

    for student in students_config:
        repo_name = student['repo_name']

        # Get grade data for this repository
        grade_info = grades_data.get(repo_name, {})

        mapped_student = {
            'repo_name': repo_name,
            'moodle_username': student['moodle_username'],
            'github_username': grade_info.get('github_username', 'Unknown'),
            'email': student['email'],
            'final_score': grade_info.get('final_score', 0.0),
            'grade': grade_info.get('grade', 'N/A')
        }

        mapped_students.append(mapped_student)

    return mapped_students


def call_moodle_api(function_name, parameters=None):
    """
    Call a Moodle Web Services API function

    Args:
        function_name: Name of the Moodle web service function
        parameters: Dictionary of parameters to pass to the function

    Returns:
        JSON response from Moodle or None if error
    """
    if parameters is None:
        parameters = {}

    url = f"{MOODLE_URL}/webservice/rest/server.php"

    params = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': function_name,
        'moodlewsrestformat': 'json'
    }

    # Add function-specific parameters
    params.update(parameters)

    try:
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Check for Moodle error messages
        if isinstance(result, dict) and 'exception' in result:
            print(f"[FAIL] Moodle API Error: {result.get('message', 'Unknown error')}")
            if 'debuginfo' in result:
                print(f"   Debug Info: {result['debuginfo']}")
            return None

        return result

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Connection Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON Decode Error: {e}")
        print(f"   Response: {response.text[:200]}")
        return None


def test_connection():
    """Test basic connection to Moodle"""
    print("\n" + "=" * 70)
    print("TEST 1: Testing Moodle Connection")
    print("=" * 70)

    result = call_moodle_api('core_webservice_get_site_info')

    if result:
        print("[OK] Connection successful!")
        print(f"   Site Name: {result.get('sitename', 'N/A')}")
        print(f"   Moodle Version: {result.get('release', 'N/A')}")
        print(f"   User: {result.get('firstname', '')} {result.get('lastname', '')}")
        print(f"   User ID: {result.get('userid', 'N/A')}")
        return True
    else:
        print("[FAIL] Connection failed!")
        return False


def test_get_course_info():
    """Test retrieving course information"""
    print("\n" + "=" * 70)
    print("TEST 2: Retrieving Course Information")
    print("=" * 70)

    result = call_moodle_api('core_course_get_courses', {
        'options[ids][0]': MOODLE_COURSE_ID
    })

    if result and len(result) > 0:
        course = result[0]
        print("[OK] Course found!")
        print(f"   Course Name: {course.get('fullname', 'N/A')}")
        print(f"   Course ID: {course.get('id', 'N/A')}")
        print(f"   Short Name: {course.get('shortname', 'N/A')}")
        return True
    else:
        print(f"[FAIL] Could not retrieve course with ID: {MOODLE_COURSE_ID}")
        return False


def test_get_enrolled_users(student_usernames=None):
    """Test retrieving enrolled users in the course using core_user_get_users"""
    print("\n" + "=" * 70)
    print("TEST 3: Retrieving Course Users")
    print("=" * 70)

    # If no usernames provided, get from config
    if student_usernames is None:
        students_config = get_student_usernames_from_config()
        student_usernames = [s['moodle_username'] for s in students_config]

    # Moodle doesn't support multiple criteria with the same key
    # So we need to make individual API calls for each user
    print(f"Searching for {len(student_usernames)} students individually...")

    all_users = []
    found_count = 0

    for username in student_usernames:
        result = call_moodle_api('core_user_get_users', {
            'criteria[0][key]': 'username',
            'criteria[0][value]': username
        })

        if result and 'users' in result and len(result['users']) > 0:
            user = result['users'][0]
            all_users.append(user)
            found_count += 1
            print(f"   [+] Found: {username} (ID: {user.get('id')})")
        else:
            print(f"   [-] Not found: {username}")

    print(f"\n[OK] Found {found_count}/{len(student_usernames)} user(s)")

    if all_users:
        print("\n   Sample users (first 5):")
        for user in all_users[:5]:
            print(f"   - ID: {user.get('id')} | Username: {user.get('username', 'N/A')} | "
                  f"Name: {user.get('firstname', '')} {user.get('lastname', '')} | "
                  f"Email: {user.get('email', 'N/A')}")
        return all_users
    else:
        print("[FAIL] No users found")
        return None


def test_get_grade_items():
    """Test retrieving grade items for the course using gradereport_user_get_grade_items"""
    print("\n" + "=" * 70)
    print("TEST 4: Retrieving Grade Items")
    print("=" * 70)

    result = call_moodle_api('gradereport_user_get_grade_items', {
        'courseid': MOODLE_COURSE_ID
    })

    if result and 'usergrades' in result:
        # Get grade items from the first user (they all have the same grade items)
        if len(result['usergrades']) > 0:
            grade_items = result['usergrades'][0].get('gradeitems', [])
            print(f"[OK] Found {len(grade_items)} grade item(s)")
            print("\n   Grade Items:")
            for item in grade_items:
                print(f"   - ID: {item.get('id')} | Name: {item.get('itemname', 'N/A')} | "
                      f"Type: {item.get('itemtype', 'N/A')}")
            return grade_items
        else:
            print("[WARN] No users found to retrieve grade items")
            return []
    else:
        print("[FAIL] Could not retrieve grade items")
        print("   This function requires at least one enrolled user in the course")
        return None


def test_get_grades(user_id=None):
    """Test retrieving grades table using gradereport_user_get_grades_table"""
    print("\n" + "=" * 70)
    print("TEST 5: Retrieving Grades Table")
    print("=" * 70)

    if user_id is None:
        print("[WARN] No user ID provided, skipping grades table test")
        return None

    result = call_moodle_api('gradereport_user_get_grades_table', {
        'courseid': MOODLE_COURSE_ID,
        'userid': user_id
    })

    if result and 'tables' in result:
        print(f"[OK] Retrieved grades table for user {user_id}")
        tables = result['tables']
        if tables:
            print(f"\n   Found {len(tables)} grade table(s)")
            # The response is HTML tables, so we'll just confirm we got data
            print("   Grades table retrieved successfully")
        return result
    else:
        print("[WARN] Could not retrieve grades table (may be normal if no grades exist yet)")
        return None


def test_update_grade(user_id, grade_value, grade_item_id=None):
    """
    Test updating a grade for a specific user using core_grades_update_grades

    Args:
        user_id: Moodle user ID
        grade_value: Grade to assign (0-100)
        grade_item_id: Grade item ID (optional, will use MOODLE_ASSIGNMENT_ID if not provided)
    """
    print("\n" + "=" * 70)
    print("TEST 6: Updating a Grade using core_grades_update_grades")
    print("=" * 70)
    print(f"   Target User ID: {user_id}")
    print(f"   Grade to Assign: {grade_value}/100")

    # IMPORTANT: For core_grades_update_grades with 'component' and 'source',
    # we need to use the ACTIVITY ID (module ID), not the grade item ID
    activity_id = MOODLE_ACTIVITY_ID
    grade_item_id_used = MOODLE_GRADE_ITEM_ID

    print(f"   Activity ID (for API): {activity_id}")
    print(f"   Grade Item ID (reference): {grade_item_id_used}")

    # Use activity ID in the activityid parameter
    result = call_moodle_api('core_grades_update_grades', {
        'source': 'mod/assign',
        'courseid': MOODLE_COURSE_ID,
        'component': 'mod_assign',
        'activityid': activity_id,  # Must use activity ID here, not grade item ID
        'itemnumber': 0,
        'grades[0][studentid]': user_id,
        'grades[0][grade]': grade_value
    })

    if result is not None:
        print("[OK] Grade update successful!")
        print(f"   Result: {result}")
        return True
    else:
        print("[FAIL] Grade update failed with core_grades_update_grades")
        print("\n   Possible reasons:")
        print("   1. Your token may not have permission to update grades")
        print("   2. The grade item ID or user ID may be incorrect")
        print("   3. The grade item may not be properly configured")
        return False


def test_alternative_grade_update(user_id, grade_value, grade_item_id=None):
    """
    Test alternative method: direct grade update using grade item ID
    This method tries to use the grade item ID directly without component/source
    """
    print("\n" + "=" * 70)
    print("TEST 7: Alternative Grade Update (Direct Grade Item)")
    print("=" * 70)

    # Use the actual grade item ID for this method
    item_id = MOODLE_GRADE_ITEM_ID
    print(f"   Using Grade Item ID: {item_id}")

    # Try direct grade item update without component/source
    result = call_moodle_api('core_grades_update_grades', {
        'source': 'manual',  # Try manual source
        'courseid': MOODLE_COURSE_ID,
        'component': 'gradeimport',
        'activityid': 0,
        'itemnumber': 0,
        'grades[0][studentid]': user_id,
        'grades[0][grade]': grade_value,
        'itemid': item_id
    })

    if result is not None:
        print("[OK] Alternative parameter configuration works!")
        return True
    else:
        print("[WARN] Alternative method also failed")
        print("   You may need to configure grade items differently in Moodle")
        return False


def batch_update_grades(mapped_students, moodle_users):
    """
    Update grades for all students in Moodle

    Args:
        mapped_students: List from map_github_to_moodle_users() with grade data
        moodle_users: List of Moodle user objects from test_get_enrolled_users()

    Returns:
        Dictionary with success/failure counts and details
    """
    print("\n" + "=" * 70)
    print("BATCH GRADE UPDATE")
    print("=" * 70)

    # Create a mapping of moodle_username to moodle_user_id
    username_to_id = {}
    for user in moodle_users:
        username_to_id[user.get('username')] = user.get('id')

    results = {
        'total': len(mapped_students),
        'success': 0,
        'failed': 0,
        'not_found': 0,
        'details': []
    }

    activity_id = MOODLE_ACTIVITY_ID

    for student in mapped_students:
        moodle_username = student['moodle_username']
        final_score = student['final_score']
        repo_name = student['repo_name']

        # Check if user exists in Moodle
        if moodle_username not in username_to_id:
            print(f"   [-] {moodle_username} - Not found in Moodle")
            results['not_found'] += 1
            results['details'].append({
                'repo_name': repo_name,
                'moodle_username': moodle_username,
                'status': 'not_found',
                'grade': final_score
            })
            continue

        moodle_user_id = username_to_id[moodle_username]

        # Update grade
        result = call_moodle_api('core_grades_update_grades', {
            'source': 'mod/assign',
            'courseid': MOODLE_COURSE_ID,
            'component': 'mod_assign',
            'activityid': activity_id,
            'itemnumber': 0,
            'grades[0][studentid]': moodle_user_id,
            'grades[0][grade]': final_score
        })

        if result is not None:
            print(f"   [+] {moodle_username} - Grade updated to {final_score}/100")
            results['success'] += 1
            results['details'].append({
                'repo_name': repo_name,
                'moodle_username': moodle_username,
                'status': 'success',
                'grade': final_score
            })
        else:
            print(f"   [-] {moodle_username} - Failed to update grade")
            results['failed'] += 1
            results['details'].append({
                'repo_name': repo_name,
                'moodle_username': moodle_username,
                'status': 'failed',
                'grade': final_score
            })

    print("\n" + "=" * 70)
    print(f"[OK] Successfully updated: {results['success']}/{results['total']}")
    print(f"[FAIL] Failed: {results['failed']}/{results['total']}")
    print(f"[WARN] Not found in Moodle: {results['not_found']}/{results['total']}")
    print("=" * 70)

    return results


# ------------------------------
# MAIN TEST EXECUTION
# ------------------------------

def main():
    """Run all Moodle integration tests and batch update student grades"""
    print("=" * 70)
    print("MOODLE WEB SERVICES INTEGRATION TEST")
    print("=" * 70)
    print(f"Moodle URL: {MOODLE_URL}")
    print(f"Course ID: {MOODLE_COURSE_ID}")
    print(f"Activity ID: {MOODLE_ACTIVITY_ID} (assignment module)")
    print(f"Grade Item ID: {MOODLE_GRADE_ITEM_ID} (for grading API)")
    print("\nNote: Activity ID and Grade Item ID are different!")
    print("      Activity ID = assignment module (from URL)")
    print("      Grade Item ID = gradebook entry (used for updating grades)")

    # Load student data from config.py and grades from student_summary.txt
    print("\n" + "=" * 70)
    print("LOADING STUDENT DATA")
    print("=" * 70)

    students_config = get_student_usernames_from_config()
    print(f"[OK] Loaded {len(students_config)} student(s) from config.py")

    grades_data = read_grades_from_individual_results()
    print(f"[OK] Loaded {len(grades_data)} grade(s) from individual result files")

    mapped_students = map_github_to_moodle_users(students_config, grades_data)
    print(f"[OK] Mapped {len(mapped_students)} student(s) with grades")

    # Show sample of mapped students
    if mapped_students:
        print("\n   Sample students (first 3):")
        for student in mapped_students[:3]:
            print(f"   - Repo: {student['repo_name']}")
            print(f"     Moodle: {student['moodle_username']} | GitHub: @{student['github_username']}")
            print(f"     Score: {student['final_score']}/100 | Grade: {student['grade']}")

    # Test 1: Connection
    if not test_connection():
        print("\n[FAIL] Basic connection failed. Please check your MOODLE_URL and MOODLE_TOKEN")
        return

    # Test 2: Course Info
    if not test_get_course_info():
        print("\n[WARN] Warning: Could not retrieve course info. Check MOODLE_COURSE_ID")

    # Test 3: Users (load from config)
    users = test_get_enrolled_users()

    # Test 4: Grade Items
    grade_items = test_get_grade_items()

    # Test 5: Grades (only if we have users)
    if users and len(users) > 0:
        test_get_grades(users[0].get('id'))

    # Batch Grade Updates
    if users and len(users) > 0 and mapped_students:
        print("\n" + "=" * 70)
        print("BATCH GRADE UPDATE")
        print("=" * 70)

        # Ask user if they want to update grades
        print(f"\n[WARN] WARNING: This will update grades for {len(mapped_students)} student(s) in Moodle")
        print("   Make sure you have reviewed the grades in student_summary.txt")
        response = input("\nDo you want to proceed with batch grade updates? (yes/no): ").strip().lower()

        if response in ['yes', 'y']:
            results = batch_update_grades(mapped_students, users)

            # Save results to file
            try:
                results_file = os.path.join(OUTPUT_DIR, "moodle_update_results.txt")
                with open(results_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("MOODLE GRADE UPDATE RESULTS\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(f"Total students: {results['total']}\n")
                    f.write(f"Successfully updated: {results['success']}\n")
                    f.write(f"Failed: {results['failed']}\n")
                    f.write(f"Not found in Moodle: {results['not_found']}\n\n")
                    f.write("=" * 80 + "\n")
                    f.write("DETAILS\n")
                    f.write("=" * 80 + "\n\n")

                    for detail in results['details']:
                        f.write(f"Repository: {detail['repo_name']}\n")
                        f.write(f"Moodle Username: {detail['moodle_username']}\n")
                        f.write(f"Status: {detail['status']}\n")
                        f.write(f"Grade: {detail['grade']}/100\n")
                        f.write("-" * 80 + "\n\n")

                print(f"\n[OK] Results saved to: {results_file}")
            except Exception as e:
                print(f"[WARN] Could not save results to file: {e}")
        else:
            print("\n[WARN] Skipping batch grade updates (user declined)")
    else:
        if not users:
            print("\n[WARN] Skipping batch grade updates (no users found in Moodle)")
        elif not mapped_students:
            print("\n[WARN] Skipping batch grade updates (no student grades loaded)")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("[OK] = Working | [FAIL] = Failed | [WARN] = Warning")
    print("\nIf all tests passed, grades have been updated in Moodle")
    print("If tests failed, check:")
    print("1. Web services are enabled in Moodle")
    print("2. Your token has the correct permissions")
    print("3. The course and assignment IDs are correct")
    print("4. Student usernames match between GitHub and Moodle")
    print("=" * 70)


if __name__ == "__main__":
    main()
