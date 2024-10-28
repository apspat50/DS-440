import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from finvader import finvader
import time

# Get the current working directory
current_dir = os.getcwd()

# Define the input and output directories as the current working directory
input_dir = current_dir
output_dir = current_dir

# Create the output directory if it doesn't exist (optional, since current_dir should always exist)
os.makedirs(output_dir, exist_ok=True)

# Function to analyze sentiment of text
def analyze_sentiment(text: str) -> float:
    sentiment_result = finvader(text, use_sentibignomics=True, use_henry=True, indicator='compound')
    return sentiment_result.get('compound', 0.0) if isinstance(sentiment_result, dict) else (sentiment_result if isinstance(sentiment_result, float) else 0.0)

# Function to fetch article content from a URL with error handling and retry logic
def fetch_article_content(url: str, retries: int = 3) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)  # Added timeout for requests
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                article_text = ' '.join([para.get_text() for para in paragraphs])
                return article_text
            else:
                print(f"Failed to fetch article from {url}: {response.status_code}")
                return ""
        except requests.exceptions.RequestException as e:
            print(f"Error fetching article from {url}, attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff before retrying
    return ""  # Return empty string if all retries fail

# Only process news.csv
input_file_path = os.path.join(input_dir, 'news.csv')
output_file_path = os.path.join(output_dir, 'news_with_sentiment.csv')

# Load the input CSV file
try:
    news_df = pd.read_csv(input_file_path)
except pd.errors.EmptyDataError:
    print(f"Skipping empty file: {input_file_path}")
    exit()
except FileNotFoundError:
    print(f"File not found: {input_file_path}")
    exit()

# Check for required columns
required_columns = ['Url', 'Title']
missing_columns = [col for col in required_columns if col not in news_df.columns]

if missing_columns:
    print(f"Missing columns {missing_columns} in news.csv")
else:
    title_sentiments = []
    content_sentiments = []
    combined_sentiments = []
    
    # Dictionary to store processed URLs and their sentiment scores
    processed_urls = {}

    # First pass to process all URLs
    for index, row in news_df.iterrows():
        url = row['Url']
        title = row['Title']
        print(f"Processing URL: {url}")

        # Fetch the content and analyze sentiment
        content = fetch_article_content(url)

        # Analyze sentiment
        title_sentiment = analyze_sentiment(title) if title else None
        content_sentiment = analyze_sentiment(content) if content else None

        # Store results
        combined_sentiment = None
        if title_sentiment is not None and content_sentiment is not None:
            combined_sentiment = (0.3 * title_sentiment) + (0.7 * content_sentiment)

        processed_urls[url] = (title_sentiment, content_sentiment, combined_sentiment)

        # Append the sentiments to the lists
        title_sentiments.append(title_sentiment if title_sentiment is not None else 0.0)
        content_sentiments.append(content_sentiment if content_sentiment is not None else 0.0)
        combined_sentiments.append(combined_sentiment if combined_sentiment is not None else 0.0)

        time.sleep(1)  # Optional delay to avoid overwhelming the server

    # Retry for URLs with empty sentiments
    for index, row in news_df.iterrows():
        url = row['Url']
        print(f"Retrying empty sentiment for URL: {url}")

        # Check if the combined sentiment is empty
        if processed_urls[url][2] is None:
            # Retry fetching content for empty sentiment
            content = fetch_article_content(url)
            content_sentiment = analyze_sentiment(content) if content else 0.0

            # Use existing title sentiment
            title_sentiment = processed_urls[url][0]

            # Recalculate combined sentiment
            if title_sentiment is not None and content_sentiment is not None:
                combined_sentiment = (0.3 * title_sentiment) + (0.7 * content_sentiment)
            else:
                combined_sentiment = None

            # Update the processed URLs dictionary
            processed_urls[url] = (title_sentiment, content_sentiment, combined_sentiment)

            # Append the sentiments to the lists again
            title_sentiments[index] = title_sentiment if title_sentiment is not None else 0.0
            content_sentiments[index] = content_sentiment if content_sentiment is not None else 0.0
            combined_sentiments[index] = combined_sentiment if combined_sentiment is not None else 0.0

            time.sleep(1)  # Optional delay to avoid overwhelming the server

    # Append sentiment results to DataFrame
    news_df['Title_Sentiment'] = title_sentiments
    news_df['Content_Sentiment'] = content_sentiments
    news_df['Combined_Sentiment'] = combined_sentiments

    # Write results to output CSV
    if os.path.isfile(output_file_path):
        if os.stat(output_file_path).st_size == 0:
            print(f"File is empty, writing new data: {output_file_path}")
            news_df.to_csv(output_file_path, index=False)
        else:
            print(f"Appending to existing file: {output_file_path}")
            existing_df = pd.read_csv(output_file_path)
            combined_df = pd.concat([existing_df, news_df], ignore_index=True)
            combined_df.to_csv(output_file_path, index=False)
    else:
        print(f"Creating new file: {output_file_path}")
        news_df.to_csv(output_file_path, index=False)

print("All sentiment analyses have been completed and saved.")
