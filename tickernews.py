import sys
from finvizfinance.quote import finvizfinance
import os
import pandas as pd

def fetch_news_for_ticker(ticker):
    output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    print(f"Fetching news for ticker: {ticker}")

    # Fetch news for the specific stock ticker using Finviz
    stock = finvizfinance(ticker)
    news_df = stock.ticker_news()

    # Convert 'Date' column to datetime format
    news_df['Date'] = pd.to_datetime(news_df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    # Filter articles from today's date
    today = pd.Timestamp('today').normalize()
    today_news_df = news_df[news_df['Date'].dt.normalize() == today]

    # Sort DataFrame by 'Date' in descending order
    today_news_df = today_news_df.sort_values(by='Date', ascending=False)

    # Define the output file path
    output_file_path = os.path.join(output_dir, f"{ticker}_today_news.csv")

    # Write today's news articles to the CSV file
    today_news_df.to_csv(output_file_path, mode='w', header=True, index=False)

    print(f"Today's news articles for {ticker} have been saved to {output_file_path}")

if __name__ == "__main__":
    # Check if a ticker argument is provided
    if len(sys.argv) < 2:
        print("Please provide a ticker symbol as an argument.")
        sys.exit(1)

    ticker = sys.argv[1]  # Get the ticker symbol from the command-line argument
    fetch_news_for_ticker(ticker)
