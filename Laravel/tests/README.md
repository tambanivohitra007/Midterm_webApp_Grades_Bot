# Laravel Event Scheduler - Standard Test Suite

This is a standard test suite to automatically grade Laravel Event Scheduler projects. These tests verify core functionality that all student projects should implement.

## Test Coverage

### 1. **EventCreationTest.php** (Basic CRUD & Relationships)
- ✅ Can create events with valid data
- ✅ Event requires title
- ✅ Event requires valid time range (start < end)
- ✅ Event belongs to Room (relationship)
- ✅ Room has many Events (relationship)

### 2. **TimeOverlapValidationTest.php** (Overlap Detection)
- ✅ Prevents complete overlap (same time)
- ✅ Prevents partial overlap (start during existing event)
- ✅ Prevents partial overlap (end during existing event)
- ✅ Prevents enveloping overlap (new event contains existing)
- ✅ Allows back-to-back events (end time = next start time)
- ✅ Allows non-overlapping events
- ✅ Different rooms don't conflict

### 3. **RoomCapacityTest.php** (Capacity Constraints)
- ✅ Can book event within capacity
- ✅ Can book event at exact capacity
- ✅ Validates participants not exceeding room capacity
- ✅ Multiple overlapping events cannot exceed total capacity
- ✅ Non-overlapping events can each use full capacity
- ✅ Validates participants is positive number

### 4. **OpeningHoursValidationTest.php** (Business Hours)
- ✅ Can book event within opening hours
- ✅ Can book at opening time
- ✅ Can book ending at closing time
- ✅ Validates event starting before opening time
- ✅ Validates event ending after closing time
- ✅ Validates event spanning outside hours
- ✅ Supports 24-hour rooms
- ✅ Validates event duration is positive

## Usage Instructions

### For Automated Grading:

1. **Copy tests to student project:**
   ```bash
   cp -r tests/ /path/to/student/project/
   ```

2. **Run tests:**
   ```bash
   cd /path/to/student/project
   php artisan test
   ```

3. **Parse results:**
   - Count passing/failing tests
   - Calculate score based on pass rate

### Expected Student Project Structure:

```
student-project/
├── app/
│   ├── Models/
│   │   ├── Event.php    (required)
│   │   ├── Room.php     (required)
│   │   └── User.php     (required)
│   └── Http/
│       └── Controllers/
├── database/
│   └── migrations/
│       ├── create_rooms_table.php
│       └── create_events_table.php
├── tests/
│   └── Feature/
│       ├── EventCreationTest.php           (copied)
│       ├── TimeOverlapValidationTest.php   (copied)
│       ├── RoomCapacityTest.php            (copied)
│       └── OpeningHoursValidationTest.php  (copied)
└── phpunit.xml
```

## Required Model Fields

### Event Model
```php
- id
- title (string, required)
- room_id (foreign key, required)
- start_time (datetime, required)
- end_time (datetime, required)
- participants (integer, required, positive)
- timestamps
```

### Room Model
```php
- id
- name (string, required)
- capacity (integer, required, positive)
- open_time (time, required)
- close_time (time, required)
- timestamps
```

### Required Relationships
```php
// Event.php
public function room() {
    return $this->belongsTo(Room::class);
}

// Room.php
public function events() {
    return $this->hasMany(Event::class);
}
```

## Scoring

Each test file has equal weight:
- **EventCreationTest**: 25%
- **TimeOverlapValidationTest**: 25%
- **RoomCapacityTest**: 25%
- **OpeningHoursValidationTest**: 25%

Individual test methods within each file contribute proportionally to that file's score.

## Customization

You can adjust the tests for your specific requirements:

1. **Modify field names** - Update field names in tests to match your assignment spec
2. **Add custom validation** - Add more test cases for specific business rules
3. **Adjust constraints** - Change capacity limits, time ranges, etc.

## Notes

- Tests use SQLite in-memory database by default (RefreshDatabase)
- Tests assume Laravel 8+ with factory() support
- All tests are independent and can run in any order
- Tests clean up after themselves (RefreshDatabase trait)

## Troubleshooting

If tests fail to run:

1. **Missing Models**: Ensure Event, Room, User models exist
2. **Missing Migrations**: Run `php artisan migrate:fresh`
3. **Missing Dependencies**: Run `composer install`
4. **Wrong Field Names**: Update test code to match student's schema
5. **PHP Version**: Ensure PHP 8.0+ is installed

## Integration with Python Grader

See `copy_and_run_tests.py` for automated test execution and scoring.
