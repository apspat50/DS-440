import pandas as pd
import os

# Path to the news_with_sentiment.csv file
input_csv_path = "news_with_sentiment.csv"

# Path to the output CSV file
output_csv_path = "average_sentiment_per_ticker.csv"

# Check and clear the output file if it exists
if os.path.exists(output_csv_path):
    try:
        os.remove(output_csv_path)
        print(f"Cleared existing file: {output_csv_path}")
    except PermissionError:
        print(f"Error: Permission denied while trying to delete {output_csv_path}.")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting the file: {e}")
else:
    print(f"No existing file found to clear: {output_csv_path}")

# Read the CSV file containing news and sentiment data
try:
    news_df = pd.read_csv(input_csv_path)
except pd.errors.EmptyDataError:
    print(f"Error: The file {input_csv_path} is empty or cannot be read.")
    exit(1)
except FileNotFoundError:
    print(f"Error: The file {input_csv_path} does not exist.")
    exit(1)

# Ensure the necessary columns exist
if 'Ticker' not in news_df.columns or 'Combined_Sentiment' not in news_df.columns:
    print(f"Error: The 'Ticker' or 'Combined_Sentiment' column is missing in {input_csv_path}.")
    exit(1)

# Group by 'Ticker' and calculate the average of the 'Combined_Sentiment' for each ticker
average_sentiments = news_df.groupby('Ticker')['Combined_Sentiment'].mean().reset_index()

# Save the result to a new CSV file
try:
    average_sentiments.to_csv(output_csv_path, index=False)
    print(f"Average sentiment for each ticker has been calculated and saved to {output_csv_path}.")
except Exception as e:
    print(f"Error: An unexpected error occurred while saving the CSV file: {e}")
