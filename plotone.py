import sys
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import subprocess 

class PlotViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Price Change vs Sentiment")
        self.setGeometry(100, 100, 800, 400)
        layout = QVBoxLayout()
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def update_plot(self, fig):
        output_html_path = "templates/price_change_vs_sentiment.html"
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        pio.write_html(fig, file=output_html_path, auto_open=False)
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(output_html_path)))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sentiment Analysis Grapher")
        self.setGeometry(500, 100, 800, 800)
        layout = QHBoxLayout()

        # Left layout for Y-axis variable selector and first plot viewer
        left_layout = QVBoxLayout()

        # Create a horizontal layout for the first plot variable selector
        variable_layout = QHBoxLayout()
        self.y_variable_selector = QComboBox()
        self.y_variable_selector.addItems(["Change", "Price", "Volume", "P/E"])
        variable_layout.addWidget(QLabel("Select Plot 1 Variable:"))
        variable_layout.addWidget(self.y_variable_selector)
        left_layout.addLayout(variable_layout)

        self.plot_viewer = PlotViewer()
        left_layout.addWidget(self.plot_viewer)

        self.plot_button = QPushButton("Generate Plot 1")
        self.plot_button.clicked.connect(self.generate_plot)
        left_layout.addWidget(self.plot_button)

        layout.addLayout(left_layout)

        # Right layout for ticker selector and second plot
        right_layout = QVBoxLayout()

        # Create a horizontal layout for the ticker selector
        ticker_layout = QHBoxLayout()
        self.ticker_selector = QComboBox()
        self.populate_ticker_selector()
        ticker_layout.addWidget(QLabel("Select Plot 2 Ticker:"))
        ticker_layout.addWidget(self.ticker_selector)
        right_layout.addLayout(ticker_layout)

        self.plot_viewer2 = PlotViewer()
        right_layout.addWidget(self.plot_viewer2)

        self.plot_button2 = QPushButton("Generate Plot 2")
        self.plot_button2.clicked.connect(self.generate_plot2)
        right_layout.addWidget(self.plot_button2)

        layout.addLayout(right_layout)
        self.setLayout(layout)


    def populate_ticker_selector(self):
        input_sentiment_csv = "average_sentiment_per_ticker.csv"
        try:
            sentiment_df = pd.read_csv(input_sentiment_csv)
            if 'Ticker' in sentiment_df.columns:
                self.ticker_selector.addItems(sentiment_df['Ticker'].unique().tolist())
            else:
                print("Error: 'Ticker' column missing in sentiment data.")
        except Exception as e:
            print(f"Error reading sentiment CSV: {e}")

    def generate_plot(self):
        input_sentiment_csv = "average_sentiment_per_ticker.csv"
        input_price_csv = "export.csv"
        y_variable = self.y_variable_selector.currentText()
        fig = create_plot(input_sentiment_csv, input_price_csv, y_variable)

        if fig:
            self.plot_viewer.update_plot(fig)

    def generate_plot2(self):
        ticker = self.ticker_selector.currentText()
        
        try:
            subprocess.run(['python', 'tickernews.py', ticker], check=True, capture_output=True, text=True)
            subprocess.run(['python', 'analyze.py', ticker], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running scripts: {e}")
            return

        # Read generated sentiment CSV file
        input_sentiment_csv = f"{ticker}_with_sentiment.csv"
        try:
            sentiment_df = pd.read_csv(input_sentiment_csv)
        except Exception as e:
            print(f"Error reading sentiment CSV: {e}")
            return
        
        if 'Date' not in sentiment_df.columns or 'Combined_Sentiment' not in sentiment_df.columns:
            print("Error: Required columns missing in sentiment data.")
            return

        # Check if there's only one article
        if len(sentiment_df) == 1:
            # Generate a single point plot if only one article is available
            fig = px.scatter(
                sentiment_df,
                x='Date',
                y='Combined_Sentiment',
                title=f'Combined Sentiment for {ticker} (Only One Article)',
                labels={'Combined_Sentiment': 'Combined Sentiment', 'Date': 'Date'},
            )
        else:
            # Generate the plot for combined sentiment over time
            fig = px.line(
                sentiment_df,
                x='Date',
                y='Combined_Sentiment',
                title=f'Combined Sentiment Over Time for {ticker}',
                labels={'Combined_Sentiment': 'Combined Sentiment', 'Date': 'Date'},
            )
        
        if fig:
            self.plot_viewer2.update_plot(fig)


def create_plot(input_sentiment_csv, input_price_csv, y_variable):
    try:
        sentiment_df = pd.read_csv(input_sentiment_csv)
        price_df = pd.read_csv(input_price_csv)
    except pd.errors.EmptyDataError as e:
        print(f"Error reading CSV: {e}")
        return None

    if 'Ticker' not in price_df.columns or y_variable not in price_df.columns:
        print(f"Error: Missing 'Ticker' or '{y_variable}' column.")
        return None

    # Clean and prepare data
    price_df['Change'] = pd.to_numeric(price_df['Change'].str.replace('%', ''), errors='coerce')
    price_df.dropna(subset=['Change'], inplace=True)

    # Merge sentiment and price data without filtering by selected ticker
    combined_df = pd.merge(sentiment_df, price_df[['Ticker', y_variable]], on='Ticker', how='inner')

    if 'Combined_Sentiment' not in combined_df.columns:
        print(f"Error: 'Combined_Sentiment' column missing.")
        return None

    # Generate Plotly scatter plot
    fig = px.scatter(
        combined_df,
        x='Combined_Sentiment',
        y=y_variable,
        text='Ticker',
        title='Price Change vs Average Sentiment',
        labels={'Combined_Sentiment': 'Average Sentiment', y_variable: y_variable},
    )

    fig.add_hline(y=0, line_color='black', line_width=1)
    fig.add_vline(x=0, line_color='black', line_width=1)
    fig.update_traces(textposition='top center', marker=dict(size=10))

    return fig

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
