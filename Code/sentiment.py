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
    if isinstance(sentiment_result, dict) and 'compound' in sentiment_result:
        return sentiment_result['compound']
    return sentiment_result if isinstance(sentiment_result, float) else 0.0

# Function to fetch article content from a URL
def fetch_article_content(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ' '.join([para.get_text() for para in paragraphs])
            return article_text
        else:
            print(f"Failed to fetch article from {url}: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error fetching article from {url}: {e}")
        return ""

# Process each CSV file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.csv') and not filename.endswith('_with_sentiment.csv'):
        input_file_path = os.path.join(input_dir, filename)
        output_file_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_with_sentiment.csv")

        try:
            news_df = pd.read_csv(input_file_path)
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {input_file_path}")
            continue

        required_columns = ['Url', 'Title']
        missing_columns = [col for col in required_columns if col not in news_df.columns]

        if missing_columns:
            print(f"Missing columns {missing_columns} in {filename}")
            continue

        title_sentiments = []
        content_sentiments = []
        combined_sentiments = []

        for index, row in news_df.iterrows():
            try:
                url = row['Url']
                title = row['Title']
                print(f"Processing URL: {url}")

                content = fetch_article_content(url)

                if content and title:
                    title_sentiment = analyze_sentiment(title)
                    content_sentiment = analyze_sentiment(content)

                    # Apply weighted combination: 30% title, 70% content
                    combined_sentiment = (0.3 * title_sentiment) + (0.7 * content_sentiment)

                    title_sentiments.append(title_sentiment)
                    content_sentiments.append(content_sentiment)
                    combined_sentiments.append(combined_sentiment)
                else:
                    title_sentiments.append(None)
                    content_sentiments.append(None)
                    combined_sentiments.append(None)

                time.sleep(1)  # Optional delay to avoid overwhelming the server
            except KeyError as e:
                print(f"Error processing row {index}: {e}")
                continue

        news_df['Title_Sentiment'] = title_sentiments
        news_df['Content_Sentiment'] = content_sentiments
        news_df['Combined_Sentiment'] = combined_sentiments

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
