from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from datetime import datetime, time
import pandas as pd
import subprocess
import os
import sys
import csv

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
        self.setGeometry(500, 300, 800, 400)

        self.layout = QVBoxLayout()

        # Welcome Message
        self.welcome_label = QLabel("Welcome to the Stock Sentiment Tool Dashboard", self)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.welcome_label)

        # Application Description
        self.description_label = QLabel("Use the buttons below to run different scripts.", self)
        self.layout.addWidget(self.description_label)

        # Horizontal layout for output areas
        self.output_layout = QHBoxLayout()

        # Left Output Area (for messages)
        self.left_output_area = QTextEdit(self)
        self.left_output_area.setReadOnly(True)
        self.output_layout.addWidget(self.left_output_area)

        # Right Output Area (for top 10 tickers)
        self.right_output_area = QTextEdit(self)
        self.right_output_area.setReadOnly(True)
        self.output_layout.addWidget(self.right_output_area)

        self.layout.addLayout(self.output_layout)

        # Button to Gather Data
        self.run_all_button = QPushButton("Gather Data", self)
        self.run_all_button.clicked.connect(self.show_loading_and_run_scripts)
        self.layout.addWidget(self.run_all_button)

        # Button to Run plotone.py
        self.run_plotone_button = QPushButton("Plot Data", self)
        self.run_plotone_button.clicked.connect(self.run_plotone)
        self.layout.addWidget(self.run_plotone_button)

        # New Button to Update Data
        self.update_data_button = QPushButton("Update Data", self)
        self.update_data_button.clicked.connect(self.run_update_script)
        self.layout.addWidget(self.update_data_button)

        self.setLayout(self.layout)

        # Check for CSV files on startup
        self.check_csv_files()

        #Schedule tasks at specific times
        self.schedule_tasks()

        self.topten()

    def schedule_tasks(self):
        """Schedule 'Gather Data' and 'Update Data' at specific times."""
        self.schedule_task(self.show_loading_and_run_scripts, time(4, 0))  # 4 AM
        self.schedule_task(self.run_update_script, time(7, 0))  # 7 AM
        self.schedule_task(self.run_update_script, time(9, 0))  # 9 AM

    def schedule_task(self, task, target_time):
        """Schedule a task to run at a specific time."""
        now = datetime.now()
        target_datetime = datetime.combine(now.date(), target_time)

        # If the target time has already passed today, schedule it for tomorrow
        if now > target_datetime:
            target_datetime = datetime.combine(now.date() + pd.Timedelta(days=1), target_time)

        delay = int((target_datetime - now).total_seconds() * 1000)  # Convert to milliseconds
        QTimer.singleShot(delay, task)

    def check_csv_files(self):
        """Check if necessary CSV files exist and run scripts if not.""" 
        if not (os.path.exists("news_with_sentiment.csv") and os.path.exists("export.csv")):
            self.left_output_area.append("Welcome! Please wait while we prepare your data. This may take a moment.")
            QTimer.singleShot(1000, self.run_initial_scripts)  # Delay for 1 second

    def run_initial_scripts(self):
        """Run initial scripts to prepare data.""" 
        scripts = [
            "export.py",
            "price.py",
            "sentiment.py",
            "compilesent.py",
        ]
        
        self.thread = ScriptRunner(scripts)
        self.thread.output_signal.connect(self.update_output)
        self.thread.finished.connect(self.on_scripts_finished)

        self.thread.start()  # Start the thread
        self.topten()

    def show_loading_and_run_scripts(self):
        """Show loading message and then run all scripts.""" 
        self.left_output_area.clear()  # Clear previous output
        self.left_output_area.append("Loading data, please wait...")

        # Disable the button while running scripts
        self.disable_buttons()

        # Use QTimer to delay the execution of scripts
        QTimer.singleShot(1000, self.run_all_scripts)  # Delay for 1 second

    def run_all_scripts(self):
        """Run all specified scripts except plotone.py and update the output area.""" 
        scripts = [
            "export.py",
            "price.py",
            "sentiment.py",
            "compilesent.py",
        ]
        
        self.thread = ScriptRunner(scripts)
        self.thread.output_signal.connect(self.update_output)
        self.thread.finished.connect(self.on_scripts_finished)

        self.thread.start() 
        self.topten()

    def run_update_script(self):
        """Run update.py and display the output in the output area.""" 
        self.left_output_area.clear()
        self.left_output_area.append("Updating data, please wait...")

        self.disable_buttons()

        QTimer.singleShot(1000, self.run_update)

    def topten(self):
        # Clear the right output area before displaying new data
        self.right_output_area.clear()

        try:
            # Check if 'average_sentiment_per_ticker.csv' exists and is not empty
            try:
                sentiment_df = pd.read_csv('average_sentiment_per_ticker.csv')
                if sentiment_df.empty:
                    raise ValueError("Sentiment data is empty.")
            except (FileNotFoundError, ValueError) as e:
                self.right_output_area.append("No sentiment data available.")
                return

            # Check if 'export.csv' exists and is not empty
            try:
                price_change_df = pd.read_csv('export.csv')
                if price_change_df.empty:
                    raise ValueError("Price change data is empty.")
            except (FileNotFoundError, ValueError) as e:
                self.right_output_area.append("No price change data available.")
                return

            # Clean the 'Change' column by removing the '%' sign and converting to numeric values
            price_change_df['Change'] = price_change_df['Change'].str.replace('%', '').astype(float)

            # Filter for tickers with a positive price change
            positive_change_df = price_change_df[price_change_df['Change'] > 0]

            # Merge the filtered dataframe with sentiment data based on 'Ticker'
            merged_df = pd.merge(sentiment_df, positive_change_df[['Ticker', 'Change']], on='Ticker')

            # Sort by Combined_Sentiment (descending)
            sorted_tickers = merged_df.sort_values(by='Combined_Sentiment', ascending=False)

            # Get the top 10 tickers with the best sentiment and positive price change
            top_10_tickers = sorted_tickers.head(10)

            if top_10_tickers.empty:
                self.right_output_area.append("No tickers match the criteria.")
            else:
                self.right_output_area.append("Top 10 Tickers with Best Sentiment and Positive Price Change:")
                self.right_output_area.append(top_10_tickers.to_string(index=False))

        except Exception as e:
            # In case any other error occurs
            self.right_output_area.append(f"Error: {e}")

    def run_update(self):
        """Helper to run the update script and re-enable buttons.""" 
        output = self.run_script("update.py")
        self.left_output_area.append(output)
        self.enable_buttons()

    def update_output(self, message):
        """Update the output area with the script message.""" 
        self.left_output_area.append(message)

    def on_scripts_finished(self):
        """Handle actions after scripts have finished running.""" 
        QMessageBox.information(self, "Done", "All scripts have been executed.")
        self.enable_buttons()

        self.topten()

    def run_plotone(self):
        """Run plotone.py and display the output in a dialog."""
        self.left_output_area.append("Plotting Ended.")

        # Run plotone.py directly
        self.run_script("plotone.py")

    def run_scripts(self, scripts):
        """Run a list of scripts sequentially."""
        for script in scripts:
            self.run_script(script)

    def run_script(self, script):
        """Run a single script and capture its output."""
        try:
            result = subprocess.run([sys.executable, script], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                self.update_output(output)
            else:
                output = result.stderr
                self.update_output(f"Error in {script}: {output}")
        except Exception as e:
            self.update_output(f"Exception while running {script}: {str(e)}")

    def disable_buttons(self):
        """Disable the buttons during script execution."""
        self.run_all_button.setDisabled(True)
        self.run_plotone_button.setDisabled(True)
        self.update_data_button.setDisabled(True)

    def enable_buttons(self):
        """Enable the buttons after script execution."""
        self.run_all_button.setDisabled(False)
        self.run_plotone_button.setDisabled(False)
        self.update_data_button.setDisabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
