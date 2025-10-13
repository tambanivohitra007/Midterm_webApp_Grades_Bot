"""
Student Grading System - Graphical User Interface (Flet)
A modern, user-friendly interface to manage the automated grading system
"""

import flet as ft
import threading
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class GradingSystemUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Student Grading System Manager"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True

        # Variables
        self.grading_process = None
        self.teams_process = None

        # UI Elements references
        self.output_column = None
        self.config_text = None
        self.status_repos = None
        self.status_graded = None
        self.status_deadline = None
        self.status_freeze = None
        self.status_bar = None
        self.grade_btn = None
        self.teams_btn = None

        # Build UI
        self.build_ui()

        # Load initial status
        self.update_status()

        # Show welcome message in console
        self.show_welcome_message()

    def build_ui(self):
        """Build the main user interface"""

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.WHITE, size=30),
                ft.Text(
                    "Student Grading System Manager",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_700,
            padding=20,
        )

        # Main content - Split into left and right panels
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        main_content = ft.Row(
            [left_panel, right_panel],
            expand=True,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # Status bar
        self.status_bar = ft.Text("Ready", size=12, color=ft.Colors.GREY_700)
        status_bar_container = ft.Container(
            content=self.status_bar,
            bgcolor=ft.Colors.GREY_200,
            padding=10,
        )

        # Main layout
        self.page.add(
            ft.Column([
                header,
                ft.Container(
                    content=main_content,
                    expand=True,
                    padding=10,
                ),
                status_bar_container
            ], spacing=0, expand=True)
        )

    def create_left_panel(self):
        """Create left panel with actions and configuration"""

        # Action buttons
        self.grade_btn = ft.ElevatedButton(
            "Grade All Students",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.run_grading,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            width=280,
            height=50,
        )

        self.teams_btn = ft.ElevatedButton(
            "Send Teams Messages",
            icon=ft.Icons.EMAIL,
            on_click=self.send_teams_messages,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            width=280,
            height=50,
        )

        verify_btn = ft.ElevatedButton(
            "Verify Email Mappings",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=self.verify_mappings,
            bgcolor=ft.Colors.ORANGE_700,
            color=ft.Colors.WHITE,
            width=280,
            height=50,
        )

        summary_btn = ft.ElevatedButton(
            "View Student Summary",
            icon=ft.Icons.ASSESSMENT,
            on_click=self.view_summary,
            bgcolor=ft.Colors.PURPLE_700,
            color=ft.Colors.WHITE,
            width=280,
            height=50,
        )

        config_btn = ft.ElevatedButton(
            "Edit Configuration",
            icon=ft.Icons.SETTINGS,
            on_click=self.open_config,
            bgcolor=ft.Colors.BLUE_GREY_700,
            color=ft.Colors.WHITE,
            width=280,
            height=50,
        )

        actions_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Actions", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.grade_btn,
                    self.teams_btn,
                    verify_btn,
                    summary_btn,
                    config_btn,
                ], spacing=10),
                padding=20,
            )
        )

        # Configuration display
        self.config_text = ft.Text(
            "Loading configuration...",
            size=11,
            font_family="Consolas",
            selectable=True,
        )

        refresh_btn = ft.ElevatedButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            on_click=lambda _: self.load_config_info(),
            width=280,
        )

        config_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Current Configuration", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Container(
                        content=self.config_text,
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=5,
                        height=250,
                    ),
                    refresh_btn,
                ], spacing=10),
                padding=20,
            )
        )

        return ft.Container(
            content=ft.Column([
                actions_card,
                config_card,
            ], spacing=10),
            width=320,
        )

    def create_right_panel(self):
        """Create right panel with console output and status"""

        # Console output with modern terminal styling
        self.output_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            auto_scroll=True,
        )

        # Terminal header bar
        terminal_header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TERMINAL, size=16, color=ft.Colors.GREEN_400),
                ft.Text(
                    "Console Output",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN_400,
                    font_family="Consolas"
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text("●", size=16, color=ft.Colors.GREEN_400),
                    tooltip="Active"
                )
            ], spacing=5),
            bgcolor="#1e1e1e",
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREEN_400)),
        )

        # Console container with gradient-like dark theme
        console_container = ft.Container(
            content=self.output_column,
            bgcolor="#0d1117",
            padding=15,
            border=ft.border.all(2, "#30363d"),
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            height=420,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
        )

        # Styled buttons
        clear_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_SWEEP, size=18, color=ft.Colors.WHITE),
                ft.Text("Clear", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=5),
            bgcolor=ft.Colors.RED_700,
            padding=10,
            border_radius=6,
            on_click=self.clear_output,
            ink=True,
            tooltip="Clear console output"
        )

        save_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD, size=18, color=ft.Colors.WHITE),
                ft.Text("Save Log", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=5),
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
            border_radius=6,
            on_click=self.save_log,
            ink=True,
            tooltip="Save console log to file"
        )

        console_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CODE, color=ft.Colors.BLUE_700, size=22),
                        ft.Text("Terminal", size=18, weight=ft.FontWeight.BOLD),
                    ], spacing=8),
                    ft.Container(height=5),
                    ft.Container(
                        content=ft.Column([
                            terminal_header,
                            console_container,
                        ], spacing=0),
                        border_radius=8,
                    ),
                    ft.Container(height=10),
                    ft.Row([clear_btn, save_btn], spacing=10),
                ], spacing=0),
                padding=20,
            ),
            elevation=4,
            expand=True,
        )

        # Status section
        self.status_repos = ft.Text("0", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        self.status_graded = ft.Text("0", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        self.status_deadline = ft.Text("Not set", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        self.status_freeze = ft.Text("Unlocked", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)

        status_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("System Status", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Repositories Found:", size=13),
                        self.status_repos,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text("Students Graded:", size=13),
                        self.status_graded,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text("Submission Deadline:", size=13),
                        self.status_deadline,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text("Grading Status:", size=13),
                        self.status_freeze,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10),
                padding=20,
            )
        )

        return ft.Container(
            content=ft.Column([
                console_card,
                status_card,
            ], spacing=10),
            expand=True,
        )

    # Action methods

    def run_grading(self, e):
        """Run the grading process"""
        if self.grading_process and self.grading_process.poll() is None:
            self.show_dialog("Warning", "Grading is already in progress!")
            return

        def confirm_grading(e):
            dialog.open = False
            self.page.update()
            self.start_grading()

        def cancel_grading(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Grading"),
            content=ft.Text("This will grade all student repositories.\n\nDo you want to continue?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_grading),
                ft.TextButton("Continue", on_click=confirm_grading),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def start_grading(self):
        """Start the grading process"""
        # Test output immediately
        self.log_output("TEST: Button clicked - this message should appear immediately!")
        self.log_output("=" * 60)
        self.log_output("Starting grading process...")
        self.log_output(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_output("=" * 60)

        self.grade_btn.disabled = True
        self.grade_btn.text = "Grading in Progress..."
        self.update_status_bar("Grading students...")
        self.page.update()

        # Run in thread
        thread = threading.Thread(target=self.execute_grading)
        thread.daemon = True
        thread.start()

        # Confirm thread started
        self.log_output("Background thread launched for grading...")

    def execute_grading(self):
        """Execute the grading script"""
        try:
            self.log_output("🚀 Launching grading subprocess...")

            # Run Main.py
            self.grading_process = subprocess.Popen(
                [sys.executable, "Main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )

            self.log_output("📡 Subprocess started, reading output...")

            # Read output line by line
            import time
            line_count = 0

            # Read from stdout
            while True:
                line = self.grading_process.stdout.readline()
                if not line:
                    # Check if process has ended
                    if self.grading_process.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue

                line_count += 1
                self.log_output(line.rstrip())

            # Read any remaining stderr
            stderr_output = self.grading_process.stderr.read()
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.log_output(f"⚠️ {line}")

            self.log_output(f"✓ Read {line_count} lines of output")

            if self.grading_process.returncode == 0:
                self.log_output("\n✅ Grading completed successfully!")
                self.page.run_thread_safe(lambda: self.show_dialog("Success", "Grading completed successfully!"))
            else:
                self.log_output(f"\n❌ Grading failed with code {self.grading_process.returncode}")
                self.page.run_thread_safe(lambda: self.show_dialog("Error", "Grading process failed. Check console for details."))

        except Exception as e:
            self.log_output(f"\n❌ Error: {str(e)}")
            self.page.run_thread_safe(lambda: self.show_dialog("Error", f"Failed to run grading:\n{str(e)}"))

        finally:
            def _reset_button():
                self.grade_btn.disabled = False
                self.grade_btn.text = "Grade All Students"
                self.update_status_bar("Ready")
                self.update_status()
                self.page.update()

            self.page.run_thread_safe(_reset_button)

    def send_teams_messages(self, e):
        """Send messages via Microsoft Teams"""
        if self.teams_process and self.teams_process.poll() is None:
            self.show_dialog("Warning", "Teams messaging is already in progress!")
            return

        # Check if grading results exist
        if not os.path.exists("cloned_repos"):
            self.show_dialog("Error", "No grading results found!\n\nPlease run grading first.")
            return

        def confirm_teams(e):
            dialog.open = False
            self.page.update()
            self.start_teams_messaging()

        def cancel_teams(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Teams Messaging"),
            content=ft.Text(
                "This will send grade reports to all students via Microsoft Teams.\n\n"
                "Make sure you have graded the students first.\n\n"
                "Do you want to continue?"
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_teams),
                ft.TextButton("Continue", on_click=confirm_teams),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def start_teams_messaging(self):
        """Start Teams messaging process"""
        self.log_output("\n" + "=" * 60)
        self.log_output("Starting Teams messaging...")
        self.log_output(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_output("=" * 60)

        self.teams_btn.disabled = True
        self.teams_btn.text = "Sending Messages..."
        self.update_status_bar("Sending Teams messages...")
        self.page.update()

        # Run in thread
        thread = threading.Thread(target=self.execute_teams_messaging)
        thread.daemon = True
        thread.start()

    def execute_teams_messaging(self):
        """Execute the Teams messaging script"""
        try:
            # Run chatMessage.py
            self.teams_process = subprocess.Popen(
                [sys.executable, "chatMessage.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )

            # Read output line by line
            for line in self.teams_process.stdout:
                self.log_output(line.rstrip())

            self.teams_process.wait()

            if self.teams_process.returncode == 0:
                self.log_output("\n✅ Messages sent successfully!")
                self.page.run_thread_safe(lambda: self.show_dialog("Success", "Teams messages sent successfully!"))
            else:
                self.log_output(f"\n❌ Messaging failed with code {self.teams_process.returncode}")
                self.page.run_thread_safe(lambda: self.show_dialog("Error", "Teams messaging failed. Check console for details."))

        except Exception as e:
            self.log_output(f"\n❌ Error: {str(e)}")
            self.page.run_thread_safe(lambda: self.show_dialog("Error", f"Failed to send messages:\n{str(e)}"))

        finally:
            def _reset_button():
                self.teams_btn.disabled = False
                self.teams_btn.text = "Send Teams Messages"
                self.update_status_bar("Ready")
                self.page.update()

            self.page.run_thread_safe(_reset_button)

    def verify_mappings(self, e):
        """Verify email mappings"""
        self.log_output("\n" + "=" * 60)
        self.log_output("Verifying email mappings...")
        self.log_output("=" * 60)

        self.update_status_bar("Verifying mappings...")

        thread = threading.Thread(target=self.execute_verification)
        thread.daemon = True
        thread.start()

    def execute_verification(self):
        """Execute verification script"""
        try:
            process = subprocess.run(
                [sys.executable, "verify_mappings.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            output = process.stdout if process.stdout else process.stderr
            # Split output by lines for better formatting
            for line in output.split('\n'):
                if line.strip():
                    self.log_output(line)

            if process.returncode == 0:
                self.page.run_thread_safe(lambda: self.show_dialog("Verification Complete", "All mappings verified successfully!"))
            else:
                self.page.run_thread_safe(lambda: self.show_dialog("Verification Issues", "Some mappings need attention. Check console for details."))

        except Exception as e:
            self.log_output(f"\n❌ Error: {str(e)}")
            self.page.run_thread_safe(lambda: self.show_dialog("Error", f"Failed to verify mappings:\n{str(e)}"))

        finally:
            self.page.run_thread_safe(lambda: self.update_status_bar("Ready"))

    def view_summary(self, e):
        """View student summary"""
        summary_file = os.path.join("cloned_repos", "student_summary.txt")

        if not os.path.exists(summary_file):
            self.show_dialog("Error", "Student summary not found!\n\nPlease run grading first.")
            return

        # Open in default text editor
        try:
            if sys.platform == "win32":
                os.startfile(summary_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", summary_file])
            else:
                subprocess.run(["xdg-open", summary_file])

            self.log_output(f"\n📊 Opened student summary: {summary_file}")
        except Exception as e:
            self.show_dialog("Error", f"Failed to open summary:\n{str(e)}")

    def open_config(self, e):
        """Open configuration file"""
        config_file = "config.py"

        if not os.path.exists(config_file):
            self.show_dialog("Error", "config.py not found!")
            return

        try:
            if sys.platform == "win32":
                os.startfile(config_file)
            elif sys.platform == "darwin":
                subprocess.run(["open", config_file])
            else:
                subprocess.run(["xdg-open", config_file])

            self.log_output(f"\n⚙ Opened configuration: {config_file}")
            self.show_dialog("Configuration", "After editing config.py, click 'Refresh' to reload the configuration.")
        except Exception as e:
            self.show_dialog("Error", f"Failed to open config:\n{str(e)}")

    # Utility methods

    def log_output(self, message):
        """Log message to output console with intelligent styling"""

        def _add_message():
            # Determine message type and color
            msg_lower = message.lower()

            if "✅" in message or "success" in msg_lower or "completed" in msg_lower:
                # Success message
                icon = "✅"
                color = "#4ade80"  # Bright green
                prefix_color = "#22c55e"
            elif "❌" in message or "error" in msg_lower or "failed" in msg_lower:
                # Error message
                icon = "❌"
                color = "#f87171"  # Bright red
                prefix_color = "#ef4444"
            elif "⚠" in message or "warning" in msg_lower:
                # Warning message
                icon = "⚠️"
                color = "#fbbf24"  # Amber
                prefix_color = "#f59e0b"
            elif message.startswith("="):
                # Separator line
                icon = ""
                color = "#6366f1"  # Indigo
                prefix_color = color
            elif "starting" in msg_lower or "running" in msg_lower:
                # Info/process message
                icon = "▶"
                color = "#60a5fa"  # Blue
                prefix_color = "#3b82f6"
            elif "time:" in msg_lower or "deadline" in msg_lower:
                # Time-related message
                icon = "🕐"
                color = "#a78bfa"  # Purple
                prefix_color = "#8b5cf6"
            elif "grading" in msg_lower or "grade" in msg_lower:
                # Grading-related
                icon = "📝"
                color = "#34d399"  # Emerald
                prefix_color = "#10b981"
            elif "repository" in msg_lower or "repo" in msg_lower:
                # Repository-related
                icon = "📦"
                color = "#f472b6"  # Pink
                prefix_color = "#ec4899"
            else:
                # Default message
                icon = "›"
                color = "#9ca3af"  # Gray
                prefix_color = "#6b7280"

            # Get timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Create styled message with timestamp
            if message.strip():
                message_row = ft.Row([
                    ft.Text(
                        f"[{timestamp}]",
                        size=10,
                        color="#4b5563",
                        font_family="Consolas",
                        weight=ft.FontWeight.W_300
                    ),
                    ft.Text(
                        icon,
                        size=11,
                        color=prefix_color if icon else color,
                    ),
                    ft.Text(
                        message.strip(),
                        size=11,
                        font_family="Consolas",
                        color=color,
                        selectable=True,
                        weight=ft.FontWeight.W_400
                    ),
                ], spacing=8)

                self.output_column.controls.append(message_row)

            # Auto-scroll to bottom and limit lines
            if len(self.output_column.controls) > 1000:  # Increased limit
                self.output_column.controls.pop(0)

            self.page.update()

        # Execute in the main UI thread
        try:
            # Try thread-safe update first
            if hasattr(self.page, 'run_thread_safe'):
                self.page.run_thread_safe(_add_message)
            else:
                # Fallback: direct update (may work in some Flet versions)
                _add_message()
        except Exception as ex:
            # Last resort: direct update
            try:
                _add_message()
            except:
                pass

    def clear_output(self, e):
        """Clear output console"""
        self.output_column.controls.clear()
        # Add a welcome message
        welcome_row = ft.Row([
            ft.Icon(ft.Icons.TERMINAL, color="#22c55e", size=16),
            ft.Text(
                "Console ready. Waiting for operations...",
                size=12,
                color="#4ade80",
                font_family="Consolas",
                italic=True
            )
        ], spacing=8)
        self.output_column.controls.append(welcome_row)
        self.page.update()

    def save_log(self, e):
        """Save console output to file"""
        def save_file(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, 'w', encoding='utf-8') as f:
                        for control in self.output_column.controls:
                            if isinstance(control, ft.Row):
                                # Extract text from each component in the row
                                line_parts = []
                                for item in control.controls:
                                    if isinstance(item, ft.Text):
                                        line_parts.append(item.value)
                                f.write(" ".join(line_parts) + "\n")
                    self.show_dialog("Success", f"Log saved to:\n{e.path}")
                except Exception as ex:
                    self.show_dialog("Error", f"Failed to save log:\n{str(ex)}")

        file_picker = ft.FilePicker(on_result=save_file)
        self.page.overlay.append(file_picker)
        self.page.update()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_picker.save_file(
            file_name=f"grading_log_{timestamp}.txt",
            allowed_extensions=["txt"]
        )

    def update_status_bar(self, message):
        """Update status bar message"""
        self.status_bar.value = message
        self.page.update()

    def load_config_info(self):
        """Load and display configuration information"""
        try:
            from config import (
                ORG_NAME,
                ASSIGNMENT_REPO_PREFIX,
                SUBMISSION_DEADLINE,
                FREEZE_GRADING,
                GRADE_COMMITS_UNTIL,
                INSTRUCTION_FOLLOWING_BONUS,
                INSTRUCTION_THRESHOLD,
                LATE_SUBMISSION_PENALTY,
                STUDENT_EMAILS
            )

            freeze_status = "🔒 Frozen" if FREEZE_GRADING else "🔓 Active"
            cutoff = GRADE_COMMITS_UNTIL if GRADE_COMMITS_UNTIL else "None"

            config_info = f"""Organization: {ORG_NAME}

Repo Prefix: {ASSIGNMENT_REPO_PREFIX}

Deadline: {SUBMISSION_DEADLINE}

Grading Status: {freeze_status}

Cutoff Date: {cutoff}

Bonus (>80%): +{INSTRUCTION_FOLLOWING_BONUS} pts

Late Penalty: -{LATE_SUBMISSION_PENALTY} pts

Students Mapped: {len(STUDENT_EMAILS)}
"""

            self.config_text.value = config_info

        except Exception as e:
            self.config_text.value = f"Error loading config:\n{str(e)}"

        self.page.update()

    def update_status(self):
        """Update status information"""
        try:
            # Load config
            self.load_config_info()

            from config import SUBMISSION_DEADLINE, FREEZE_GRADING, STUDENT_EMAILS

            # Update status labels
            self.status_repos.value = str(len(STUDENT_EMAILS))
            self.status_deadline.value = SUBMISSION_DEADLINE

            if FREEZE_GRADING:
                self.status_freeze.value = "🔒 Frozen"
                self.status_freeze.color = ft.Colors.RED_700
            else:
                self.status_freeze.value = "🔓 Active"
                self.status_freeze.color = ft.Colors.GREEN_700

            # Check for graded students
            if os.path.exists("cloned_repos"):
                graded_count = len([
                    d for d in os.listdir("cloned_repos")
                    if os.path.isdir(os.path.join("cloned_repos", d))
                    and os.path.exists(os.path.join("cloned_repos", d, "result.txt"))
                ])
                self.status_graded.value = str(graded_count)

            self.page.update()

        except Exception as e:
            self.log_output(f"Error updating status: {str(e)}")

    def show_dialog(self, title, message):
        """Show a dialog message"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_welcome_message(self):
        """Display welcome message in console"""
        welcome_banner = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ROCKET_LAUNCH, color="#60a5fa", size=16),
                    ft.Text(
                        "Student Grading System v1.0",
                        size=13,
                        color="#60a5fa",
                        font_family="Consolas",
                        weight=ft.FontWeight.BOLD
                    )
                ], spacing=8),
                ft.Row([
                    ft.Text("│", color="#30363d", size=12),
                    ft.Text(
                        "System initialized and ready for operations",
                        size=11,
                        color="#4ade80",
                        font_family="Consolas",
                    )
                ], spacing=8),
                ft.Row([
                    ft.Text("│", color="#30363d", size=12),
                    ft.Text(
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        size=11,
                        color="#9ca3af",
                        font_family="Consolas",
                    )
                ], spacing=8),
                ft.Divider(height=1, color="#30363d"),
            ], spacing=5)
        )
        self.output_column.controls.append(welcome_banner)
        self.page.update()


def main(page: ft.Page):
    """Main entry point"""
    GradingSystemUI(page)


if __name__ == "__main__":
    ft.app(target=main)
