"""
Verification script to check if all student repositories are mapped to emails.
"""

import sys
import io
from github import Github

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from config import (
    GITHUB_TOKEN,
    ORG_NAME,
    ASSIGNMENT_REPO_PREFIX,
    STUDENT_EMAILS,
    GITHUB_USERNAME_TO_EMAIL
)

def main():
    print("="*80)
    print("STUDENT EMAIL MAPPING VERIFICATION")
    print("="*80)

    # Connect to GitHub
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(ORG_NAME)

    # Get all matching repositories
    repos = [repo for repo in org.get_repos() if repo.name.startswith(ASSIGNMENT_REPO_PREFIX)]

    print(f"\nFound {len(repos)} repositories")
    print(f"Mapped {len(STUDENT_EMAILS)} students in STUDENT_EMAILS")
    print()

    # Check if all repos are mapped
    missing_mappings = []
    verified_mappings = []

    for repo in repos:
        repo_name = repo.name
        if repo_name in STUDENT_EMAILS:
            email = STUDENT_EMAILS[repo_name]
            if email and email.strip():
                verified_mappings.append((repo_name, email))
                print(f"✅ {repo_name}")
                print(f"   → {email}")
            else:
                missing_mappings.append(repo_name)
                print(f"❌ {repo_name}")
                print(f"   → EMPTY EMAIL!")
        else:
            missing_mappings.append(repo_name)
            print(f"❌ {repo_name}")
            print(f"   → NOT MAPPED!")
        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Verified: {len(verified_mappings)}/{len(repos)} repositories")

    if missing_mappings:
        print(f"❌ Missing/Empty: {len(missing_mappings)} repositories")
        print("\nRepositories needing attention:")
        for repo_name in missing_mappings:
            print(f"  - {repo_name}")
    else:
        print("✅ All repositories are properly mapped!")

    print()
    print("="*80)
    print("READY FOR GRADING")
    print("="*80)

    if not missing_mappings:
        print("✅ Configuration is complete!")
        print("✅ You can now run: python Main.py")
        print("✅ After grading, send messages with: python chatMessage.py")
    else:
        print("⚠️  Please add missing email mappings in config.py before grading")

    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
