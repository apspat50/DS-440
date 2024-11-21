# Finviz-Sentiment-Analysis

# Stock Sentiment Analysis and Visualization

This repository contains Python scripts for analyzing and visualizing stock news sentiment and price data. The project involves fetching news data using the FinViz API, analyzing sentiment, exporting stock prices, and generating interactive visualizations.

## Project Overview

1. **`analyze.py`**: Fetches the latest news articles and analyzes sentiment for a stock ticker from FinViz and saves them to CSV files.
2. **`compilesent.py`**: Calculates the average sentiment score for each ticker. 
3. **`export.py`**: Exports stock news data from FinViz to a CSV file.
4. **`main.py`**: Runs the main application. 
5. **`plotone.py`**: Plots the average sentiment score for each ticker vs. whatever other variable the user chooses. Plots the daily news sentiment score over time based off the ticker chosen by the user. 
6. **`price.py`**: Fetches pricing data for the tickers found in export.py.
7. **`sentiment.py`**: Analyzes the sentiment from the news articles from export.py.
8. **`tickernews.py`**: Fetches today's news for a selected ticker. 
9. **`update.py`**: Checks newly produced news articles and updates them to the list of news articles. 
10. **`updatesent.py`**: Calculate the new news articles sentiment score. 

## Setup

1. **Install Dependencies**:
   Ensure you have the required Python packages installed. You can install them from your terminal using pip:
   ```bash
   pip install pandas
   pip install requests
   pip install beautifulsoup4
   pip install finvader
   pip install PyQt5
   pip install PyQtWebEngine
   pip install plotly
   pip install finvizfinance

Update FinViz API Token:

Update the export.py script with your FinViz API token. Delete my API token and put your Finviz API token after this part of the URL code "https://elite.finviz.com/news_export.ashx?v=3&auth=". 

Script Details

**main.py**
**plotone.py**
**analyze.py**
**compilesent.py**
**price.py**
**sentiment.py**
**tickernews.py**
**update.py**
**updatesent.py**
**export.py**
Fetches news articles for specified stock tickers using the FinViz API and saves them to CSV files.

python get_news.py

Script Details:

Fetches news articles for tickers listed in the tickers variable.
Saves today's articles to individual CSV files for each ticker.
Checks if files already exist and appends data as needed.

## Notes:

Adjust time intervals in the schedule_tasks section of main.py to fit your needs.
Make sure you have the necessary API tokens and permissions to access the FinViz data.
For any issues or feature requests, please open an issue on this repository.

## Acknowledgments:

FinViz API
Finviz Finance
BeautifulSoup
Matplotlib
PyQt5
Plotly
FinVader
