import sys
import subprocess
import os
import time
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class ScriptRunner(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, scripts):
        super().__init__()
        self.scripts = scripts

    def run(self):
        for script in self.scripts:
            self.output_signal.emit(f"Running {script}...")
            output = self.run_script(script)
            self.output_signal.emit(output)
            self.output_signal.emit("-" * 80)  # Separator for clarity

        self.output_signal.emit("Data ready. You can now run plotone.py.")

    def run_script(self, script_name):
        """Run a Python script and return the output."""
        try:
            result = subprocess.run(['python', script_name], check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error running {script_name}: {e.stderr}"

class PlotOneDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotone Output")
        self.setGeometry(150, 150, 600, 400)

        self.layout = QVBoxLayout()

        # Output Area for plotone.py
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        # Button to Return to Main Menu
        self.return_button = QPushButton("Return to Main Menu", self)
        self.return_button.clicked.connect(self.close)
        self.layout.addWidget(self.return_button)

        self.setLayout(self.layout)

    def display_output(self, output):
        """Display the output of plotone.py."""
        self.output_area.clear()
        self.output_area.append(output)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Welcome to the Stock Sentiment Tool")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Welcome Message
        self.welcome_label = QLabel("Welcome to the Stock Sentiment Tool Dashboard", self)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.welcome_label)

        # Application Description
        self.description_label = QLabel("Use the buttons below to run different scripts.", self)
        self.layout.addWidget(self.description_label)

        # Output Area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        # Button to Run All Scripts Except plotone.py
        self.run_all_button = QPushButton("Run All Scripts Except plotone.py", self)
        self.run_all_button.clicked.connect(self.show_loading_and_run_scripts)
        self.layout.addWidget(self.run_all_button)

        # Button to Run plotone.py
        self.run_plotone_button = QPushButton("Run plotone.py", self)
        self.run_plotone_button.clicked.connect(self.run_plotone)
        self.layout.addWidget(self.run_plotone_button)

        self.setLayout(self.layout)

        # Check for CSV files on startup
        self.check_csv_files()

        # Start the update thread
        self.start_update_thread()

    def check_csv_files(self):
        """Check if necessary CSV files exist and run scripts if not."""
        if not (os.path.exists("news_with_sentiment.csv") and os.path.exists("export.csv")):
            self.output_area.append("Welcome! Please wait while we prepare your data. This may take a moment.")
            QTimer.singleShot(1000, self.run_initial_scripts)  # Delay for 1 second

    def run_initial_scripts(self):
        """Run initial scripts to prepare data."""
        scripts = [
            "export.py",
            "price.py",
            "sentiment.py",
            "compilesent.py",
            # "plotone.py" is intentionally excluded
        ]
        
        self.thread = ScriptRunner(scripts)
        self.thread.output_signal.connect(self.update_output)
        self.thread.finished.connect(self.on_scripts_finished)

        self.thread.start()  # Start the thread

    def show_loading_and_run_scripts(self):
        """Show loading message and then run all scripts."""
        self.output_area.clear()  # Clear previous output
        self.output_area.append("Loading data, please wait...")

        # Disable the button while running scripts
        self.run_all_button.setEnabled(False)

        # Use QTimer to delay the execution of scripts
        QTimer.singleShot(1000, self.run_all_scripts)  # Delay for 1 second

    def run_all_scripts(self):
        """Run all specified scripts except plotone.py and update the output area."""
        scripts = [
            "export.py",
            "price.py",
            "sentiment.py",
            "compilesent.py",
            # "plotone.py" is intentionally excluded
        ]
        
        self.thread = ScriptRunner(scripts)
        self.thread.output_signal.connect(self.update_output)
        self.thread.finished.connect(self.on_scripts_finished)

        self.thread.start()  # Start the thread

    def update_output(self, message):
        """Update the output area with the script message."""
        self.output_area.append(message)

    def on_scripts_finished(self):
        """Handle actions after scripts have finished running."""
        QMessageBox.information(self, "Done", "All scripts have been executed.")
        self.run_all_button.setEnabled(True)  # Re-enable the button

    def run_plotone(self):
        """Run plotone.py and display the output in a dialog."""        
        output = self.run_script("plotone.py")

        self.plotone_dialog = PlotOneDialog()
        self.plotone_dialog.display_output(output)
        self.plotone_dialog.show()

    def run_script(self, script_name):
        """Run a Python script and return the output."""
        try:
            result = subprocess.run(['python', script_name], check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error running {script_name}: {e.stderr}"

    def start_update_thread(self):
        """Start a thread to check for updates every 2 minutes."""
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True  # Allows the thread to exit when the main program exits
        self.update_thread.start()

    def update_loop(self):
        """Loop to check for updates."""
        while True:
            time.sleep(120)  # Wait for 2 minutes
            self.check_for_updates()

    def check_for_updates(self):
        """Check if there are new articles and update news.csv if necessary."""
        if not os.path.exists("news.csv"):
            self.output_area.append("news.csv does not exist. Please run export.py first.")
            return

        # Run the update.py script
        update_output = self.run_script("update.py")
        self.output_area.append(update_output)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
