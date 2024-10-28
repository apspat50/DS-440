import pandas as pd

# Path to the news_with_sentiment.csv file
input_csv_path = "news_with_sentiment.csv"

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
output_csv_path = "average_sentiment_per_ticker.csv"
average_sentiments.to_csv(output_csv_path, index=False)

print(f"Average sentiment for each ticker has been calculated and saved to {output_csv_path}.")
