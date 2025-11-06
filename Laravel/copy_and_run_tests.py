"""
Laravel Test Suite Runner
Copies standard tests to student projects and executes them
"""

import os
import subprocess
import json
import shutil
import re
from pathlib import Path


class LaravelTestRunner:
    """Handles copying and running PHPUnit tests on Laravel projects"""
    
    def __init__(self, test_suite_path, student_project_path):
        """
        Args:
            test_suite_path: Path to the standard test suite directory
            student_project_path: Path to the student's Laravel project
        """
        self.test_suite_path = Path(test_suite_path)
        self.student_project_path = Path(student_project_path)
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'test_details': [],
            'score': 0,
            'raw_output': ''
        }
    
    def check_prerequisites(self):
        """Check if student project has required files"""
        checks = {
            'laravel_project': False,
            'composer_json': False,
            'phpunit_xml': False,
            'vendor_directory': False,
            'models_exist': False
        }
        
        # Check for Laravel indicators
        checks['composer_json'] = (self.student_project_path / 'composer.json').exists()
        checks['phpunit_xml'] = (self.student_project_path / 'phpunit.xml').exists()
        checks['vendor_directory'] = (self.student_project_path / 'vendor').exists()
        
        # Check for required models
        models_dir = self.student_project_path / 'app' / 'Models'
        if models_dir.exists():
            required_models = ['Event.php', 'Room.php', 'User.php']
            found_models = [f.name for f in models_dir.glob('*.php')]
            checks['models_exist'] = any(m in found_models for m in required_models)
        
        checks['laravel_project'] = all([
            checks['composer_json'],
            (self.student_project_path / 'artisan').exists()
        ])
        
        return checks
    
    def install_dependencies(self):
        """Run composer install if vendor directory doesn't exist"""
        try:
            if not (self.student_project_path / 'vendor').exists():
                print("[INFO] Installing Composer dependencies...")
                result = subprocess.run(
                    ['composer', 'install', '--no-interaction', '--quiet'],
                    cwd=self.student_project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return result.returncode == 0
            return True
        except FileNotFoundError:
            print(f"[WARNING] Composer not found. Skipping dependency installation.")
            print(f"[INFO] Tests will attempt to run with existing dependencies.")
            # Check if vendor exists anyway
            return (self.student_project_path / 'vendor').exists()
        except Exception as e:
            print(f"[WARNING] Could not install dependencies: {e}")
            return False
    
    def copy_tests(self):
        """Copy test files to student project"""
        try:
            # Create tests/Feature directory if it doesn't exist
            target_dir = self.student_project_path / 'tests' / 'Feature'
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all test files
            source_dir = self.test_suite_path / 'Feature'
            if not source_dir.exists():
                print(f"[ERROR] Test suite not found at: {source_dir}")
                return False
            
            copied_files = []
            for test_file in source_dir.glob('*Test.php'):
                target_file = target_dir / test_file.name
                shutil.copy2(test_file, target_file)
                copied_files.append(test_file.name)
                print(f"[COPIED] {test_file.name}")
            
            return len(copied_files) > 0
            
        except Exception as e:
            print(f"[ERROR] Failed to copy tests: {e}")
            return False
    
    def run_tests(self):
        """Execute PHPUnit tests and capture results"""
        try:
            print("[RUNNING] Executing PHPUnit tests...")
            
            # Try different commands based on what's available
            commands_to_try = [
                ['php', 'artisan', 'test', '--stop-on-failure'],
                ['php', 'artisan', 'test'],
                ['./vendor/bin/phpunit', '--stop-on-failure'],
                ['vendor\\bin\\phpunit.bat', '--stop-on-failure'],  # Windows
            ]
            
            result = None
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=self.student_project_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0 or 'Tests:' in result.stdout:
                        break
                except FileNotFoundError:
                    continue
            
            if result is None:
                print("[ERROR] Could not find PHP or test runner")
                return False
            
            self.results['raw_output'] = result.stdout + result.stderr
            
            # Parse output
            self._parse_test_output(result.stdout)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("[ERROR] Tests timed out after 120 seconds")
            self.results['errors'] += 1
            return False
        except Exception as e:
            print(f"[ERROR] Failed to run tests: {e}")
            self.results['errors'] += 1
            return False
    
    def _parse_test_output(self, output):
        """Parse PHPUnit output to extract test results"""
        # Look for test summary pattern: "Tests: 15 passed"
        # or "Tests: 10 passed, 5 failed"
        
        # Pattern for newer PHPUnit versions
        summary_pattern = r'Tests:\s+(\d+)\s+passed'
        failed_pattern = r'(\d+)\s+failed'
        
        passed_match = re.search(summary_pattern, output)
        failed_match = re.search(failed_pattern, output)
        
        if passed_match:
            self.results['passed'] = int(passed_match.group(1))
        
        if failed_match:
            self.results['failed'] = int(failed_match.group(1))
        
        # Total tests
        self.results['total_tests'] = self.results['passed'] + self.results['failed']
        
        # Calculate score (0-100)
        if self.results['total_tests'] > 0:
            self.results['score'] = round(
                (self.results['passed'] / self.results['total_tests']) * 100
            )
        
        # Extract individual test details
        # Pattern: "✓ test_name_here"
        test_pattern = r'[✓✗]\s+(.+?)(?:\s+\d+ms)?$'
        for line in output.split('\n'):
            match = re.search(test_pattern, line.strip())
            if match:
                test_name = match.group(1).strip()
                passed = '✓' in line
                self.results['test_details'].append({
                    'name': test_name,
                    'passed': passed
                })
    
    def generate_report(self):
        """Generate a detailed test report"""
        report = {
            'summary': {
                'total_tests': self.results['total_tests'],
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'score': self.results['score'],
                'pass_rate': f"{self.results['score']}%"
            },
            'test_details': self.results['test_details'],
            'raw_output': self.results['raw_output']
        }
        return report
    
    def run_full_test_suite(self):
        """Main method to run the complete testing process"""
        print(f"\n{'='*70}")
        print(f"Testing Laravel Project: {self.student_project_path.name}")
        print('='*70)
        
        # Step 1: Check prerequisites
        print("\n[STEP 1] Checking prerequisites...")
        checks = self.check_prerequisites()
        
        if not checks['laravel_project']:
            print("[ERROR] Not a valid Laravel project")
            return None
        
        print("[OK] Laravel project detected")
        
        if not checks['models_exist']:
            print("[WARNING] Required models (Event, Room, User) may be missing")
        
        # Step 2: Install dependencies
        print("\n[STEP 2] Checking dependencies...")
        if not checks['vendor_directory']:
            if not self.install_dependencies():
                print("[WARNING] Could not install dependencies, tests may fail")
        else:
            print("[OK] Dependencies already installed")
        
        # Step 3: Copy tests
        print("\n[STEP 3] Copying test suite...")
        if not self.copy_tests():
            print("[ERROR] Failed to copy tests")
            return None
        
        print("[OK] Tests copied successfully")
        
        # Step 4: Run tests
        print("\n[STEP 4] Running tests...")
        success = self.run_tests()
        
        # Step 5: Generate report
        print("\n[STEP 5] Generating report...")
        report = self.generate_report()
        
        # Display results
        print(f"\n{'='*70}")
        print("TEST RESULTS")
        print('='*70)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Score: {report['summary']['score']}/100")
        print('='*70)
        
        return report


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python copy_and_run_tests.py <student_project_path>")
        print("\nExample:")
        print("  python copy_and_run_tests.py cloned_repos/event-scheduler-student1")
        sys.exit(1)
    
    # Path to standard test suite
    test_suite_path = Path(__file__).parent / 'tests'
    
    # Path to student project
    student_project_path = Path(sys.argv[1])
    
    if not student_project_path.exists():
        print(f"[ERROR] Student project not found: {student_project_path}")
        sys.exit(1)
    
    # Run tests
    runner = LaravelTestRunner(test_suite_path, student_project_path)
    report = runner.run_full_test_suite()
    
    if report:
        # Save report to JSON
        report_file = student_project_path / 'test_results.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n[SAVED] Test results saved to: {report_file}")


if __name__ == '__main__':
    main()
