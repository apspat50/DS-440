import sys
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, QObject

# Create a custom signal class
class Communicate(QObject):
    stock_clicked = pyqtSignal(str)  # Signal to emit the clicked stock ticker

# Function to create the plot and save it as HTML
def create_plot(input_sentiment_csv, input_price_csv, y_variable, stock_clicked_signal):
    # Read the CSV file containing average sentiment data
    try:
        sentiment_df = pd.read_csv(input_sentiment_csv)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_sentiment_csv} is empty or cannot be read.")
        return None

    # Read the CSV file containing stock price data
    try:
        price_df = pd.read_csv(input_price_csv)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_price_csv} is empty or cannot be read.")
        return None

    # Ensure 'Ticker' and the selected variable exist in price_df
    if 'Ticker' not in price_df.columns or y_variable not in price_df.columns:
        print(f"Error: The 'Ticker' or '{y_variable}' column is missing in {input_price_csv}.")
        return None

    # Clean the 'Change' column: remove percentage signs and convert to numeric
    price_df['Change'] = price_df['Change'].str.replace('%', '', regex=False)  # Remove percentage signs
    price_df['Change'] = pd.to_numeric(price_df['Change'], errors='coerce')  # Convert to numeric

    # Drop any rows in price_df with NaN values in the selected variable
    price_df.dropna(subset=['Change'], inplace=True)

    # Merge the two DataFrames on 'Ticker' to combine sentiment and price change data
    combined_df = pd.merge(sentiment_df, price_df[['Ticker', y_variable]], on='Ticker', how='inner')

    # Ensure 'Combined_Sentiment' exists in the merged DataFrame
    if 'Combined_Sentiment' not in combined_df.columns:
        print(f"Error: The 'Combined_Sentiment' column is missing in the combined data.")
        return None

    # Create an interactive scatter plot with Plotly
    fig = px.scatter(
        combined_df,
        x='Combined_Sentiment',
        y=y_variable,
        text='Ticker',
        title='Price Change vs Average Sentiment',
        labels={'Combined_Sentiment': 'Average Sentiment', y_variable: y_variable},
    )

    # Add vertical and horizontal lines for quadrants
    fig.add_hline(y=0, line_color='black', line_width=1)
    fig.add_vline(x=0, line_color='black', line_width=1)

    # Show hover text for Tickers
    fig.update_traces(textposition='top center')

    # Register a click event
    fig.update_traces(marker=dict(size=10),
                      selector=dict(mode='markers+text'))
    fig.for_each_trace(lambda trace: trace.on_click(
        lambda trace, points: stock_clicked_signal.emit(points['text'][0])
    ))

    return fig  # Return the figure object instead of saving it

class PlotViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Price Change vs Sentiment")
        self.setGeometry(100, 100, 800, 600)

        # Layout for the viewer
        layout = QVBoxLayout()

        # Create a web view
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.setLayout(layout)

    def update_plot(self, fig):
        """Update the plot in the viewer."""
        # Ensure the templates directory exists
        output_html_path = "templates/price_change_vs_sentiment.html"
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)

        # Save the figure as an HTML file
        pio.write_html(fig, file=output_html_path, auto_open=False)
        
        # Load the updated plot in the web view
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(output_html_path)))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dynamic Y-Axis Plotter")
        self.setGeometry(100, 100, 400, 200)

        # Layout for the main window
        layout = QVBoxLayout()

        # ComboBox for selecting Y-axis variable
        self.y_variable_selector = QComboBox()
        self.y_variable_selector.addItems(["Price", "Change", "Volume", "P/E"])  # Specified variables
        layout.addWidget(QLabel("Select Y-axis Variable:"))
        layout.addWidget(self.y_variable_selector)

        # Create the plot viewer
        self.plot_viewer = PlotViewer()
        layout.addWidget(self.plot_viewer)

        # Button to generate plot
        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.clicked.connect(self.generate_plot)
        layout.addWidget(self.plot_button)

        # Create signal instance
        self.communicate = Communicate()
        self.communicate.stock_clicked.connect(self.open_second_plot)

        self.setLayout(layout)

    def generate_plot(self):
        # Path to the CSV files
        input_sentiment_csv = "average_sentiment_per_ticker.csv"
        input_price_csv = "export.csv"

        # Get the selected Y-axis variable
        y_variable = self.y_variable_selector.currentText()

        # Create the plot with the selected Y variable
        fig = create_plot(input_sentiment_csv, input_price_csv, y_variable, self.communicate.stock_clicked)

        if fig:  # If the plot was created successfully
            self.plot_viewer.update_plot(fig)  # Update the viewer with the new plot

    def open_second_plot(self, ticker):
        """Open the second plot based on the clicked stock ticker."""
        print(f"Opening second plot for ticker: {ticker}")
        # Call your second plotting script (plottwo.py) here
        # For example:
        os.system(f"python plottwo.py {ticker}")  # Adjust this line based on how your second script accepts the ticker

if __name__ == "__main__":
    # Start the PyQt application
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
