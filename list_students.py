"""
Helper script to list all student repositories and their GitHub usernames.
This helps you create the STUDENT_EMAILS mapping in config.py.
"""

from github import Github
from config import GITHUB_TOKEN, ORG_NAME, ASSIGNMENT_REPO_PREFIX

def main():
    print("="*80)
    print("STUDENT REPOSITORY LISTING")
    print("="*80)
    print(f"Organization: {ORG_NAME}")
    print(f"Looking for repos starting with: {ASSIGNMENT_REPO_PREFIX}")
    print("="*80 + "\n")

    # Connect to GitHub
    g = Github(GITHUB_TOKEN)
    org = g.get_organization(ORG_NAME)

    # Get all matching repositories
    repos = [repo for repo in org.get_repos() if repo.name.startswith(ASSIGNMENT_REPO_PREFIX)]

    if not repos:
        print("⚠️  No repositories found matching the prefix.")
        return

    print(f"Found {len(repos)} student repositories:\n")

    # Prepare mapping template
    mapping_lines = []

    for repo in repos:
        try:
            # Try to get the primary contributor (student)
            contributors = list(repo.get_contributors())
            if contributors:
                # Get the contributor with most commits
                contributors.sort(key=lambda x: x.contributions, reverse=True)
                github_username = contributors[0].login
                contributor_name = contributors[0].name or github_username
            else:
                github_username = "unknown"
                contributor_name = "Unknown"

            # Print info
            print(f"Repository: {repo.name}")
            print(f"  GitHub Username: @{github_username}")
            print(f"  Contributor Name: {contributor_name}")
            print(f"  Repository URL: {repo.html_url}")
            print()

            # Add to mapping template
            mapping_lines.append(f'    "{repo.name}": "",  # @{github_username} - {contributor_name}')

        except Exception as e:
            print(f"  ⚠️  Error getting info: {e}")
            mapping_lines.append(f'    "{repo.name}": "",  # Error getting username')
            print()

    # Generate config.py template
    print("\n" + "="*80)
    print("COPY THIS TO config.py STUDENT_EMAILS:")
    print("="*80 + "\n")

    print("STUDENT_EMAILS = {")
    for line in mapping_lines:
        print(line)
    print("}")

    print("\n" + "="*80)
    print("INSTRUCTIONS:")
    print("="*80)
    print("1. Copy the STUDENT_EMAILS dictionary above")
    print("2. Paste it into config.py, replacing the existing STUDENT_EMAILS")
    print("3. Fill in each student's university email address")
    print("4. The GitHub username is shown in comments for reference")
    print()
    print("Example:")
    print('    "midterm-exam-atm-johndoe": "john.doe@university.edu",  # @johndoe - John Doe')
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure config.py exists and has valid GitHub credentials.")
