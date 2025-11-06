# 🚀 Quick Start - Laravel Test Suite

## One-Time Setup ✅

```bash
# Your standard test suite is ready at:
Laravel/tests/Feature/
├── EventCreationTest.php
├── TimeOverlapValidationTest.php
├── RoomCapacityTest.php
└── OpeningHoursValidationTest.php
```

## Test Single Student

```bash
# Method 1: Python script (recommended)
python Laravel/copy_and_run_tests.py cloned_repos/event-scheduler-student1

# Method 2: Manual
cp -r Laravel/tests/* cloned_repos/event-scheduler-student1/tests/
cd cloned_repos/event-scheduler-student1
php artisan test
```

## Test All Students (Loop)

```python
# Add to Laravel_grader.py
from pathlib import Path
from Laravel.copy_and_run_tests import LaravelTestRunner

# In your grading loop:
test_suite_path = Path('Laravel/tests')
runner = LaravelTestRunner(test_suite_path, laravel_path)
test_report = runner.run_full_test_suite()

if test_report:
    functionality_score = test_report['summary']['score'] * 0.3  # 30% weight
    total += functionality_score
```

## What You Get

- **28 tests** covering all requirements
- **Automatic scoring** (0-100)
- **Detailed reports** (JSON + console)
- **Fair grading** - same tests for everyone

## Test Coverage

| Category | Tests | What It Checks |
|----------|-------|----------------|
| Event Creation | 5 | CRUD, validation, relationships |
| Time Overlap | 7 | Conflict detection, edge cases |
| Room Capacity | 6 | Capacity limits, cumulative booking |
| Opening Hours | 10 | Business hours, time validation |

## Scoring Options

### Option 1: Tests Only (100%)
```python
final_score = test_report['summary']['score']  # 0-100
```

### Option 2: Mixed (Static 70% + Tests 30%)
```python
static_score = static_analysis_score * 0.7
test_score = test_report['summary']['score'] * 0.3
final_score = static_score + test_score
```

### Option 3: Tests as Bonus (Static + up to 30% bonus)
```python
final_score = min(static_score + (test_report['summary']['score'] * 0.3), 100)
```

## Customization

```php
// Edit Laravel/tests/Feature/EventCreationTest.php
// Change field names to match your assignment:

// If you use 'attendees' instead of 'participants':
'participants' => 20,  →  'attendees' => 20,

// If you use 'venue_id' instead of 'room_id':
'room_id' => $this->room->id,  →  'venue_id' => $this->venue->id,
```

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Model not found" | Update `use App\Models\Event;` to match student's namespace |
| "Tests timeout" | Increase timeout in `copy_and_run_tests.py` line 170 |
| "Database errors" | Student needs to run `php artisan migrate:fresh` |
| "No tests executed" | Check tests copied to `tests/Feature/` directory |

## Expected Student Requirements

✅ Laravel 8+  
✅ Models: Event, Room, User  
✅ Migrations created  
✅ Relationships defined  
✅ composer.json exists  

## Files Created for You

```
Laravel/
├── tests/Feature/              ← 4 test files (28 tests total)
├── tests/README.md             ← Test documentation
├── copy_and_run_tests.py       ← Automation script
├── USAGE_GUIDE.md              ← Detailed guide
└── QUICK_START.md              ← This file
```

## Next Action

**Try it on one student project:**

```bash
# Test it now!
python Laravel/copy_and_run_tests.py cloned_repos/event-scheduler-Peeranat-Ks/Event-Scheduler
```

**Expected Output:**
```
Testing Laravel Project: Event-Scheduler
[OK] Laravel project detected
[OK] Tests copied successfully
[RUNNING] Executing PHPUnit tests...
Total Tests: 28
Passed: XX
Score: XX/100
```

## Integration Template

```python
# Add this function to Laravel_grader.py

def run_functionality_tests(laravel_path):
    """Run PHPUnit tests and return score"""
    from pathlib import Path
    from Laravel.copy_and_run_tests import LaravelTestRunner
    
    test_suite = Path('Laravel/tests')
    runner = LaravelTestRunner(test_suite, laravel_path)
    report = runner.run_full_test_suite()
    
    if report and report['summary']['total_tests'] > 0:
        return {
            'score': report['summary']['score'],
            'passed': report['summary']['passed'],
            'total': report['summary']['total_tests'],
            'remarks': [f"{report['summary']['passed']}/{report['summary']['total_tests']} tests passed"]
        }
    
    return {'score': 0, 'remarks': ['Tests could not run']}

# In grade_project():
test_result = run_functionality_tests(path)
results['Functionality Tests'] = test_result
total += test_result['score'] * 0.3  # 30% weight
```

---

**Questions? Check:**
- `USAGE_GUIDE.md` - Full documentation
- `tests/README.md` - Test details
- Test files - See actual assertions
