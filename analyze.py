import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from finvader import finvader
import time
import sys

# Ensure we have a ticker symbol from the command line
if len(sys.argv) < 2:
    print("Usage: python this_script.py <ticker>")
    sys.exit(1)

# Get the ticker from the command-line argument
ticker = sys.argv[1]

current_dir = os.getcwd()
input_dir = current_dir
output_dir = current_dir
os.makedirs(output_dir, exist_ok=True)

def analyze_sentiment(text: str) -> float:
    sentiment_result = finvader(text, use_sentibignomics=True, use_henry=True, indicator='compound')
    if isinstance(sentiment_result, dict) and 'compound' in sentiment_result:
        return sentiment_result['compound']
    return sentiment_result if isinstance(sentiment_result, float) else 0.0

def fetch_article_content(url: str, retries: int = 3) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for attempt in range(retries):
        try:
            print(f"Fetching {url}, Attempt: {attempt + 1}")
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                return ' '.join([para.get_text() for para in paragraphs])
            else:
                print(f"Failed to fetch article from {url}: {response.status_code}")
                time.sleep(1)
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Error fetching article from {url}: {e}")
            time.sleep(1)
    return ""

input_file_name = f"{ticker}_today_news.csv"
input_file_path = os.path.join(input_dir, input_file_name)
output_file_path = os.path.join(output_dir, f"{ticker}_with_sentiment.csv")

# Verify input file exists
if not os.path.isfile(input_file_path):
    print(f"News file for ticker '{ticker}' does not exist: {input_file_path}")
    sys.exit(1)

print(f"Processing file for ticker '{ticker}': {input_file_path}")

try:
    news_df = pd.read_csv(input_file_path)
except pd.errors.EmptyDataError:
    print(f"Skipping empty file: {input_file_path}")
    sys.exit(1)

required_columns = ['Link', 'Title']
missing_columns = [col for col in required_columns if col not in news_df.columns]

if missing_columns:
    print(f"Missing columns {missing_columns} in {input_file_name}")
    sys.exit(1)

title_sentiments = []
content_sentiments = []
combined_sentiments = []

for index, row in news_df.iterrows():
    try:
        url = row['Link']
        title = row['Title']
        print(f"Processing URL: {url}")

        content = fetch_article_content(url)

        if content and title:
            title_sentiment = analyze_sentiment(title)
            content_sentiment = analyze_sentiment(content)
            combined_sentiment = (0.3 * title_sentiment) + (0.7 * content_sentiment)

            title_sentiments.append(title_sentiment)
            content_sentiments.append(content_sentiment)
            combined_sentiments.append(combined_sentiment)
        else:
            title_sentiments.append(0.0)
            content_sentiments.append(0.0)
            combined_sentiments.append(0.0)

        time.sleep(1)
    except KeyError as e:
        print(f"Error processing row {index}: {e}")
        continue

news_df['Title_Sentiment'] = title_sentiments
news_df['Content_Sentiment'] = content_sentiments
news_df['Combined_Sentiment'] = combined_sentiments

# Clear output file if it exists
if os.path.isfile(output_file_path):
    print(f"Clearing existing file: {output_file_path}")
    with open(output_file_path, 'w'):
        pass

print(f"Creating new file: {output_file_path}")
news_df.to_csv(output_file_path, index=False)

print(f"Sentiment analysis completed and saved for ticker '{ticker}'.")
