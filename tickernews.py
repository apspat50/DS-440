from finvizfinance.quote import finvizfinance
import os
import pandas as pd

def fetch_news_for_ticker(ticker):
    # Define the directory to save the CSV files relative to the current script's location
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print(f"Fetching news for ticker: {ticker}")

    # Fetch news for the specific stock ticker using Finviz
    stock = finvizfinance(ticker)
    news_df = stock.ticker_news()

    # Convert 'Date' column to datetime format
    news_df['Date'] = pd.to_datetime(news_df['Date'], format='%m/%d/%Y %I:%M:%S %p')

    # Filter articles from today's date
    today = pd.Timestamp('today').normalize()  # Normalize to remove time part
    today_news_df = news_df[news_df['Date'].dt.normalize() == today]

    # Sort DataFrame by 'Date' in descending order
    today_news_df = today_news_df.sort_values(by='Date', ascending=False)

    # Define the output file path
    output_file_path = os.path.join(output_dir, f"{ticker}_today_news.csv")

    # Check if file exists and is empty
    file_exists = os.path.exists(output_file_path)
    is_empty = file_exists and os.path.getsize(output_file_path) == 0

    # Determine if header should be written based on file existence and content
    if file_exists and not is_empty:
        header = False  # Do not write header if file already exists and is not empty
    else:
        header = True  # Write header if file does not exist or is empty

    # Save the filtered DataFrame to a CSV file, appending if it already exists
    today_news_df.to_csv(output_file_path, mode='a', header=header, index=False)

    print(f"Today's news articles for {ticker} have been saved to {output_file_path}")
