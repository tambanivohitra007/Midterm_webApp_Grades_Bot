# Moodle Integration Setup Guide

This guide explains how to set up automatic grade uploading to Moodle from the grading system.

## Prerequisites

- Administrative access to your Moodle site
- Python `requests` library installed: `pip install requests`

## Step 1: Enable Web Services in Moodle

1. Login to Moodle as an administrator
2. Navigate to: **Site Administration → Server → Web Services → Overview**
3. Click through each step in the overview:
   - ✅ Enable web services
   - ✅ Enable protocols (REST recommended)
   - ✅ Create a specific user (optional, can use your admin account)
   - ✅ Check user capability (ensure user has grade update permissions)
   - ✅ Select a service (create a custom service or use existing)
   - ✅ Add functions to the service
   - ✅ Select a specific user and create a token
   - ✅ Enable developer documentation

## Step 2: Enable Required Web Service Functions

Navigate to: **Site Administration → Server → Web Services → External services**

Create a new service or edit an existing one, and add these functions:

### Required Functions:
- `core_webservice_get_site_info` - Basic connection test
- `core_course_get_courses` - Retrieve course information
- `core_enrol_get_enrolled_users` - Get list of enrolled students
- `mod_assign_get_assignments` - Get assignments in a course
- `mod_assign_get_grades` - Retrieve existing grades
- `mod_assign_save_grade` - Update assignment grades (PRIMARY METHOD)

### Alternative Functions (if above don't work):
- `core_grades_update_grades` - Alternative grade update method
- `gradereport_user_get_grade_items` - Get grade items

## Step 3: Create a Web Service Token

1. Navigate to: **Site Administration → Server → Web Services → Manage tokens**
2. Click "Add"
3. Select the user (yourself or dedicated service account)
4. Select the service you created
5. Click "Save changes"
6. **Copy the token** - you'll need this for config.py

## Step 4: Find Your Course and Assignment IDs

### Finding Course ID:
1. Go to your course in Moodle
2. Look at the URL: `https://your-moodle.edu/course/view.php?id=123`
3. The number after `id=` is your **Course ID** (e.g., 123)

### Finding Assignment ID:
1. Go to the assignment in Moodle
2. Click "View all submissions" or go to assignment settings
3. Look at the URL: `https://your-moodle.edu/mod/assign/view.php?id=456`
4. The number after `id=` is your **Assignment ID** (e.g., 456)

## Step 5: Configure config.py

Edit your `config.py` file and add the Moodle configuration:

```python
# Moodle Web Services Configuration
MOODLE_URL = "https://moodle.apiu.edu"  # Your Moodle site URL (no trailing slash)
MOODLE_TOKEN = "abc123def456..."  # Your web service token
MOODLE_COURSE_ID = 123  # Your course ID
MOODLE_ASSIGNMENT_ID = 456  # Your assignment/grade item ID
```

## Step 6: Test the Connection

Run the test script to verify everything is working:

```bash
python MoodleIntegration.py
```

The script will test:
1. ✅ Basic connection to Moodle
2. ✅ Retrieving course information
3. ✅ Getting enrolled users
4. ✅ Fetching assignments
5. ✅ Reading grades
6. ✅ Updating grades (with your permission)

## Step 7: Troubleshooting

### Error: "Access control exception"
- Your token doesn't have sufficient permissions
- Add more capabilities to the service role
- Required capabilities:
  - `webservice/rest:use`
  - `moodle/grade:edit`
  - `mod/assign:grade`

### Error: "Invalid token"
- Double-check your token in config.py
- Ensure there are no extra spaces
- Verify the token hasn't expired

### Error: "Course not found"
- Verify the course ID is correct
- Ensure your user is enrolled/has access to the course

### Error: "Function not found"
- The web service function isn't enabled
- Go back to Step 2 and add the required functions

### Warning: "No users found"
- The course might be empty
- Check enrollment settings
- Verify students are enrolled in the course

## Step 8: Create Username Mapping

You need to map GitHub usernames to Moodle usernames. Add to your `config.py`:

```python
# Map GitHub usernames to Moodle usernames
GITHUB_USERNAME_TO_MOODLE = {
    "github-user1": "moodle-user1",
    "github-user2": "moodle-user2",
    # Add more mappings...
}
```

Or if students use the same username on both platforms, this step may not be needed.

## Alternative: Get Student Moodle IDs

You can also map directly to Moodle user IDs:

```python
# Map GitHub usernames to Moodle User IDs
GITHUB_USERNAME_TO_MOODLE_ID = {
    "github-user1": 12345,  # Moodle user ID
    "github-user2": 12346,
    # Add more mappings...
}
```

To find Moodle user IDs, run the test script and check the "Enrolled Users" section.

## Next Steps

Once the test script runs successfully:
1. You can integrate automatic grade upload into `Main.py`
2. Or create a separate script that reads `student_summary.txt` and uploads grades
3. Consider adding error handling and logging for production use

## Security Notes

⚠️ **Important Security Considerations:**
- Never commit your `config.py` with real tokens to GitHub
- Keep your web service token secure (treat it like a password)
- Consider using environment variables for sensitive data
- Regularly rotate your tokens
- Use a dedicated service account with minimal permissions (not your admin account)

## Support

If you encounter issues:
1. Check Moodle logs: **Site Administration → Reports → Logs**
2. Enable debugging: **Site Administration → Development → Debugging**
3. Check web service logs: **Site Administration → Server → Web Services → API documentation**
4. Test API calls in the Moodle API documentation interface

## References

- [Moodle Web Services Documentation](https://docs.moodle.org/en/Web_services)
- [Moodle API Documentation](https://docs.moodle.org/dev/Web_services)
- [Creating Web Service Tokens](https://docs.moodle.org/en/Using_web_services)
