import pandas as pd
import requests
import os
import time

# Path to the news_with_sentiment.csv file and the output CSV
input_csv_path = "news_with_sentiment.csv"
output_csv_path = "export.csv"

# Read the CSV file containing tickers
try:
    news_df = pd.read_csv(input_csv_path)
except pd.errors.EmptyDataError:
    print(f"Error: The file {input_csv_path} is empty or cannot be read.")
    exit(1)

# Ensure the 'Ticker' column exists in the dataframe
if 'Ticker' not in news_df.columns:
    print(f"Error: The 'Ticker' column is missing in {input_csv_path}.")
    exit(1)

# Get unique tickers from the 'Ticker' column
tickers = news_df['Ticker'].unique()

# Finviz URL template with placeholder for the ticker
URL_TEMPLATE = "https://elite.finviz.com/export.ashx?t={ticker}&auth=ab4e8b66-99af-4c54-b834-10d199e1e3d5"

# If export.csv exists, read it and get a list of tickers already exported
if os.path.exists(output_csv_path):
    try:
        export_df = pd.read_csv(output_csv_path)
        exported_tickers = export_df['Ticker'].unique()  # Get tickers from the exported file
    except pd.errors.EmptyDataError:
        print(f"Warning: The file {output_csv_path} is empty or cannot be read.")
        exported_tickers = []
else:
    exported_tickers = []

# Function to export data from Finviz and append to a CSV file
def export_finviz_data(ticker, output_file):
    # Replace placeholder with actual ticker
    url = URL_TEMPLATE.format(ticker=ticker)
    print(f"Requesting data for ticker: {ticker} from {url}")
    
    try:
        # Make the HTTP request to Finviz
        response = requests.get(url)
        if response.status_code == 200:
            # Save the response content to the CSV file
            with open(output_file, "ab") as f:  # Use 'ab' to append to the file
                f.write(response.content)
            print(f"Data for ticker {ticker} appended to {output_file}.")
        elif response.status_code == 429:  # Too Many Requests - rate limit exceeded
            print(f"Rate limit exceeded for ticker {ticker}. Waiting 1 second before retrying...")
            time.sleep(1)  # Sleep for 1 second if rate limit is exceeded
        else:
            print(f"Failed to fetch data for ticker {ticker}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")

# If export.csv doesn't exist, create it with headers
if not os.path.exists(output_csv_path):
    with open(output_csv_path, "wb") as f:
        f.write(b"")

# Sequentially process each ticker and add a sleep time between requests
for ticker in tickers:
    if ticker not in exported_tickers:
        export_finviz_data(ticker, output_csv_path)
        time.sleep(1)  # Sleep for 1 second between requests to avoid hitting rate limits
    else:
        print(f"Ticker {ticker} already exported, skipping.")

print("All tickers processed.")
