import pandas as pd
import requests
import os
import time

# Path to the news_with_sentiment.csv file and the output CSV
input_csv_path = "news.csv"
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

# Function to export data from Finviz
def export_finviz_data(ticker):
    # Replace placeholder with actual ticker
    url = URL_TEMPLATE.format(ticker=ticker)
    print(f"Requesting data for ticker: {ticker} from {url}")
    
    try:
        # Make the HTTP request to Finviz
        response = requests.get(url)
        if response.status_code == 200:
            # Convert the response content to a DataFrame
            data = pd.read_csv(StringIO(response.content.decode('utf-8')))
            data['Ticker'] = ticker  # Add the Ticker column to the DataFrame
            return data
        elif response.status_code == 429:  # Too Many Requests - rate limit exceeded
            print(f"Rate limit exceeded for ticker {ticker}. Waiting 1 second before retrying...")
            time.sleep(1)  # Sleep for 1 second if rate limit is exceeded
            return export_finviz_data(ticker)  # Retry fetching the data
        else:
            print(f"Failed to fetch data for ticker {ticker}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")
        return None

# If export.csv exists, read it into a DataFrame
if os.path.exists(output_csv_path):
    try:
        export_df = pd.read_csv(output_csv_path)
    except pd.errors.EmptyDataError:
        print(f"Warning: The file {output_csv_path} is empty or cannot be read.")
        export_df = pd.DataFrame()  # Create an empty DataFrame if export file is empty
else:
    export_df = pd.DataFrame()  # Create an empty DataFrame if export file does not exist

# Sequentially process each ticker and add a sleep time between requests
for ticker in tickers:
    # Fetch data for the current ticker
    finviz_data = export_finviz_data(ticker)
    
    if finviz_data is not None:
        # Check if the ticker already exists in the exported DataFrame
        if ticker in export_df['Ticker'].values:
            # Update existing rows
            existing_row_index = export_df[export_df['Ticker'] == ticker].index[0]
            print(f"Updating data for ticker: {ticker}")
            export_df.loc[existing_row_index] = finviz_data.iloc[0]  # Update the existing row
        else:
            # Append new data
            print(f"Adding new ticker data for: {ticker}")
            export_df = pd.concat([export_df, finviz_data], ignore_index=True)  # Append new data

    # Sleep for 1 second between requests to avoid hitting rate limits
    time.sleep(1)

# Write the updated DataFrame to the CSV file
if not export_df.empty:
    export_df.to_csv(output_csv_path, index=False, header=True)  # Write with header only if DataFrame is not empty
    print(f"Data exported successfully to {output_csv_path}.")
else:
    print("No data to export.")

print("All tickers processed.")
