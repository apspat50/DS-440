import requests
import os
import csv
import subprocess

# Define the URL for fetching the news data
URL = "https://elite.finviz.com/news_export.ashx?v=3&auth=ab4e8b66-99af-4c54-b834-10d199e1e3d5"

# Define any required headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_all_news():
    """Fetch all news articles from FinViz."""
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        lines = response.content.decode('utf-8').splitlines()
        return list(csv.DictReader(lines))
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return []

def read_existing_news(file_path):
    """Read existing news articles from a CSV file and return a set of unique entries based on 'Date' and 'Title'."""
    existing_news = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                existing_news.add((row['Date'], row['Title'], row['Ticker']))  # Unique identifier for each article
    return existing_news

def split_articles_by_ticker(news_data):
    """Split articles with multiple tickers into separate entries."""
    separated_articles = []
    for article in news_data:
        tickers = article['Ticker'].split(',')
        for ticker in tickers:
            new_article = article.copy()
            new_article['Ticker'] = ticker.strip()
            separated_articles.append(new_article)
    return separated_articles

def filter_new_entries(update_news, existing_news):
    """Filter out entries in update_news that already exist in existing_news."""
    return [article for article in update_news if (article['Date'], article['Title'], article['Ticker']) not in existing_news]

def update_news_csv(file_path, news_data):
    """Update the specified CSV file with the provided news data."""
    if news_data:  # Check if there is any new data to write
        with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = news_data[0].keys()  # Use the field names from the news data
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for article in news_data:
                writer.writerow(article)
        print(f"Updated {file_path} with {len(news_data)} new articles. File saved at: {file_path}")
    else:
        print(f"No new articles to update in {file_path}.")

def run_sentiment_analysis(input_file):
    """Run sentiment.py on the update.csv file and append the results to news_with_sentiment.csv."""
    try:
        result = subprocess.run(['python', 'updatesent.py', input_file], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running sentiment analysis: {e.stderr}")

def run_compile():
    """Run compile.py to finalize the data processing."""
    try:
        result = subprocess.run(['python', 'compilesent.py'], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running compile.py: {e.stderr}")

def main():
    news_file_path = "news_with_sentiment.csv"
    update_file_path = "update.csv"

    # Clear update.csv before running the script
    open(update_file_path, 'w').close()

    # Fetch all news articles
    all_news = fetch_all_news()
    if not all_news:
        print("No news available.")
        return

    # Read existing news articles from news_with_sentiment.csv
    existing_news = read_existing_news(news_file_path)

    # Split articles by ticker and filter out articles already in news_with_sentiment.csv
    separated_news = split_articles_by_ticker(all_news)
    new_entries = filter_new_entries(separated_news, existing_news)

    # Update update.csv with only the new articles
    print(f"Saving {len(new_entries)} new articles to update.csv...")
    update_news_csv(update_file_path, new_entries)

    # Run sentiment analysis and append results to news_with_sentiment.csv if there are new entries
    if new_entries:
        print("Running sentiment analysis on new articles...")
        run_sentiment_analysis(update_file_path)

        # Run compile.py after sentiment analysis is complete
        print("Running compile.py...")
        run_compile()
    else:
        print("No new articles to analyze.")

if __name__ == "__main__":
    main()
