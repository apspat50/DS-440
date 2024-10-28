import requests
import os
import csv
from datetime import datetime

# Define the URL for fetching the news data
URL = "https://elite.finviz.com/news_export.ashx?v=3&auth=ab4e8b66-99af-4c54-b834-10d199e1e3d5"

# Define any required headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_current_news():
    """Fetch current news articles from FinViz."""
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
    """Read existing news articles from the CSV file."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        return list(csv.DictReader(csv_file))

def is_news_up_to_date(current_news, existing_news):
    """Check if the current news is newer than the existing news."""
    if not existing_news:
        return False  # No existing news means we need to update
    
    # Convert the publish time strings to datetime objects for comparison
    existing_news_times = {article['Date']: article for article in existing_news}
    latest_existing_time = max(datetime.strptime(date, "%m/%d/%Y %H:%M:%S %p") for date in existing_news_times.keys())
    
    for article in current_news:
        article_time = datetime.strptime(article['Date'], "%m/%d/%Y %H:%M:%S %p")
        if article_time > latest_existing_time:
            return False  # Newer article found
    
    return True  # No new articles

def update_news_csv(file_path, current_news):
    """Update the news.csv file with the current news articles."""
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = current_news[0].keys()  # Use the field names from the current news
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for article in current_news:
            writer.writerow(article)
    print(f"Updated news.csv with new articles. File saved at: {file_path}")

def run_scripts():
    """Run the necessary scripts to update the rest of the files."""
    scripts = [
        "price.py",
        "sentiment.py",
        "compilesent.py",
        # Add more scripts as needed
    ]
    
    for script in scripts:
        try:
            result = subprocess.run(['python', script], check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e.stderr}")

def main():
    news_file_path = "news.csv"  # Adjust the path if needed

    # Fetch current news articles
    current_news = fetch_current_news()
    if not current_news:
        print("No current news available to compare.")
        return

    # Read existing news articles from the file
    existing_news = read_existing_news(news_file_path)

    # Check if news is up to date
    if is_news_up_to_date(current_news, existing_news):
        print("News is up to date. No updates necessary.")
    else:
        print("New articles found. Updating news.csv...")
        update_news_csv(news_file_path, current_news)
        run_scripts()

if __name__ == "__main__":
    main()
