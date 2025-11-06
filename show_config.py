"""
Configuration Display Tool
Shows which configuration values are used by each grading system
"""

from config import (
    # Shared
    GITHUB_TOKEN, ORG_NAME, OUTPUT_DIR, OPENAI_API_KEY, MODEL_NAME,
    MOODLE_URL, MOODLE_TOKEN,
    
    # ATM Banking System
    ATM_ASSIGNMENT_REPO_PREFIX, ATM_MOODLE_COURSE_ID, 
    ATM_MOODLE_ACTIVITY_ID, ATM_MOODLE_GRADE_ITEM_ID,
    
    # Laravel Event Management
    LARAVEL_ASSIGNMENT_REPO_PREFIX, LARAVEL_MOODLE_COURSE_ID,
    LARAVEL_MOODLE_ACTIVITY_ID, LARAVEL_MOODLE_GRADE_ITEM_ID,
)

def mask_token(token):
    """Mask sensitive token for display"""
    if not token or len(token) < 10:
        return "***"
    return f"{token[:6]}...{token[-4:]}"

def print_section(title, configs):
    """Print a configuration section"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    
    for key, value in configs.items():
        if 'TOKEN' in key or 'SECRET' in key or 'API_KEY' in key:
            display_value = mask_token(value)
        else:
            display_value = value
        print(f"{key:30s}: {display_value}")

def main():
    print("\n" + "="*70)
    print("UNIFIED GRADING SYSTEM - CONFIGURATION")
    print("="*70)
    
    # Shared Configuration
    print_section("SHARED CONFIGURATION", {
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "ORG_NAME": ORG_NAME,
        "OUTPUT_DIR": OUTPUT_DIR,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "MODEL_NAME": MODEL_NAME,
        "MOODLE_URL": MOODLE_URL,
        "MOODLE_TOKEN": MOODLE_TOKEN,
    })
    
    # ATM Banking System
    print_section("ATM BANKING SYSTEM (Main.py)", {
        "ASSIGNMENT_REPO_PREFIX": ATM_ASSIGNMENT_REPO_PREFIX,
        "MOODLE_COURSE_ID": ATM_MOODLE_COURSE_ID,
        "MOODLE_ACTIVITY_ID": ATM_MOODLE_ACTIVITY_ID,
        "MOODLE_GRADE_ITEM_ID": ATM_MOODLE_GRADE_ITEM_ID,
    })
    
    # Laravel Event Management
    print_section("LARAVEL EVENT MANAGEMENT (Laravel_grader.py)", {
        "ASSIGNMENT_REPO_PREFIX": LARAVEL_ASSIGNMENT_REPO_PREFIX,
        "MOODLE_COURSE_ID": LARAVEL_MOODLE_COURSE_ID,
        "MOODLE_ACTIVITY_ID": LARAVEL_MOODLE_ACTIVITY_ID,
        "MOODLE_GRADE_ITEM_ID": LARAVEL_MOODLE_GRADE_ITEM_ID,
    })
    
    # Warnings
    print(f"\n{'='*70}")
    print("  CONFIGURATION WARNINGS")
    print(f"{'='*70}")
    
    warnings = []
    
    if LARAVEL_MOODLE_COURSE_ID == 0 or LARAVEL_MOODLE_GRADE_ITEM_ID == 0:
        warnings.append("⚠️  Laravel Moodle IDs not configured (set to 0)")
        warnings.append("   Update LARAVEL_MOODLE_* values in config.py for Moodle integration")
    
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_github_token_here":
        warnings.append("❌ GitHub token not configured")
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_key_here":
        warnings.append("❌ OpenAI API key not configured")
    
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("✅ All configurations appear to be set")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
