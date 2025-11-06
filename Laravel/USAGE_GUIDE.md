# Laravel Test Suite - Usage Guide

## Overview

This directory contains a **standard test suite** for automatically testing and grading Laravel Event Scheduler projects. Instead of creating tests for each student individually, you create ONE set of tests based on your assignment requirements, then run them against all student projects.

## Directory Structure

```
Laravel/
├── tests/
│   ├── Feature/
│   │   ├── EventCreationTest.php           # Tests basic CRUD & relationships
│   │   ├── TimeOverlapValidationTest.php   # Tests overlap detection logic
│   │   ├── RoomCapacityTest.php            # Tests capacity constraints
│   │   └── OpeningHoursValidationTest.php  # Tests business hours validation
│   └── README.md                           # Test documentation
├── copy_and_run_tests.py                   # Python script to automate testing
└── USAGE_GUIDE.md                          # This file
```

## How It Works

### Step 1: Create Standard Tests (Done! ✅)

The test suite is already created and includes:
- **28+ individual test cases** covering all requirements
- Tests for relationships, validation, constraints, business logic
- Reusable across ALL student projects

### Step 2: Run Tests on Student Projects

Two ways to use the tests:

#### Option A: Manual Testing (One Student)

```bash
# Copy tests to student project
cp -r Laravel/tests/* /path/to/student/project/tests/

# Run tests
cd /path/to/student/project
php artisan test

# View results
# Tests: 28 passed (15 assertions)
```

#### Option B: Automated Testing (All Students)

```bash
# Run Python script
python Laravel/copy_and_run_tests.py cloned_repos/event-scheduler-student1

# Output:
# [COPIED] EventCreationTest.php
# [COPIED] TimeOverlapValidationTest.php
# [COPIED] RoomCapacityTest.php
# [COPIED] OpeningHoursValidationTest.php
# [RUNNING] Executing PHPUnit tests...
# Total Tests: 28
# Passed: 25
# Failed: 3
# Score: 89/100
```

### Step 3: Integrate with Laravel_grader.py

Add test execution to your existing grader:

```python
# In Laravel_grader.py, add:
from Laravel.copy_and_run_tests import LaravelTestRunner

def grade_project(repo, path):
    results = {}
    total = 0
    
    # ... existing static checks ...
    
    # NEW: Run actual tests
    test_suite_path = Path('Laravel/tests')
    runner = LaravelTestRunner(test_suite_path, path)
    test_report = runner.run_full_test_suite()
    
    if test_report:
        # Add test score to results
        test_score = test_report['summary']['score'] * 0.3  # 30% of grade
        results['Functionality Tests'] = {
            'score': round(test_score),
            'remarks': [
                f"{test_report['summary']['passed']}/{test_report['summary']['total_tests']} tests passed",
                f"Pass rate: {test_report['summary']['pass_rate']}"
            ]
        }
        total += test_score
    
    # ... rest of grading ...
```

## What Gets Tested

### ✅ Event Creation (5 tests)
- Can create events with valid data
- Event requires title
- Event requires valid time range
- Event belongs to Room
- Room has many Events

### ✅ Time Overlap Detection (7 tests)
- Prevents complete overlap
- Prevents partial overlap (start)
- Prevents partial overlap (end)
- Prevents enveloping overlap
- Allows back-to-back events
- Allows non-overlapping events
- Different rooms don't conflict

### ✅ Room Capacity (6 tests)
- Can book within capacity
- Can book at exact capacity
- Validates exceeding capacity
- Multiple overlapping events validation
- Non-overlapping events can use full capacity
- Validates positive participants

### ✅ Opening Hours (10 tests)
- Can book within hours
- Can book at opening time
- Can book ending at closing time
- Validates starting before opening
- Validates ending after closing
- Validates spanning outside hours
- Supports 24-hour rooms
- Validates positive duration
- Validates time format consistency

## Scoring

### Default Weighting:
- Static Code Analysis: 70% (existing checks)
- Functionality Tests: 30% (new tests)

### Test Score Calculation:
```
Test Score = (Passed Tests / Total Tests) × 100
Example: 25/28 passed = 89/100
```

## Customization

### Adjust for Your Assignment

If your assignment uses different field names or requirements:

1. **Edit test files** in `Laravel/tests/Feature/`
2. **Update field names** (e.g., `participants` → `attendees`)
3. **Add custom rules** (e.g., different capacity limits)
4. **Remove tests** that don't apply

Example:
```php
// If your Event model uses 'attendees' instead of 'participants'
'participants' => 20,  // Change to:
'attendees' => 20,
```

## Prerequisites

Students must have:
- ✅ Laravel 8+ project
- ✅ `Event` and `Room` models
- ✅ Database migrations created
- ✅ `composer.json` and dependencies installed
- ✅ `phpunit.xml` configuration

## Troubleshooting

### "Tests failed to run"
**Cause:** Missing dependencies or broken Laravel installation

**Solution:**
```bash
cd student-project
composer install
php artisan migrate:fresh
php artisan test
```

### "Models not found"
**Cause:** Student used different model names or namespaces

**Solution:** Update test imports:
```php
use App\Models\Event;  // Change to student's namespace
use App\Models\Booking;  // If they named it differently
```

### "No tests executed"
**Cause:** Tests weren't copied or wrong directory

**Solution:** Verify tests are in `student-project/tests/Feature/`

### "Database errors"
**Cause:** Migrations not run or wrong schema

**Solution:**
```bash
php artisan migrate:fresh --seed
```

## Benefits

### ✅ Fair Grading
- All students tested against same criteria
- No bias or inconsistency
- Objective pass/fail results

### ✅ Time Saving
- Write tests ONCE, reuse forever
- Automated execution and scoring
- No manual testing required

### ✅ Better Feedback
- Students see which tests fail
- Clear expectations
- Learn from test cases

### ✅ Verifies Functionality
- Not just code presence, but actual working code
- Catches broken implementations
- Tests edge cases and constraints

## Example Output

```
======================================================================
Testing Laravel Project: event-scheduler-student1
======================================================================

[STEP 1] Checking prerequisites...
[OK] Laravel project detected

[STEP 2] Checking dependencies...
[OK] Dependencies already installed

[STEP 3] Copying test suite...
[COPIED] EventCreationTest.php
[COPIED] TimeOverlapValidationTest.php
[COPIED] RoomCapacityTest.php
[COPIED] OpeningHoursValidationTest.php
[OK] Tests copied successfully

[STEP 4] Running tests...
[RUNNING] Executing PHPUnit tests...

[STEP 5] Generating report...

======================================================================
TEST RESULTS
======================================================================
Total Tests: 28
Passed: 25
Failed: 3
Score: 89/100
======================================================================

[SAVED] Test results saved to: test_results.json
```

## Next Steps

1. **Test the test suite** on a working Laravel project
2. **Adjust field names** if your assignment differs
3. **Run on one student project** to verify it works
4. **Integrate with Laravel_grader.py** for full automation
5. **Grade all students** with one command!

## Questions?

- See `tests/README.md` for detailed test documentation
- Check individual test files for specific assertions
- Modify tests to match your exact requirements
