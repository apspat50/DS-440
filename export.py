import requests
import os
import csv

# Define the URL for fetching the news data
URL = "https://elite.finviz.com/news_export.ashx?v=3&auth=ab4e8b66-99af-4c54-b834-10d199e1e3d5"

# Define any required headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_and_export_news():
    try:
        # Fetch the CSV data from the URL
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Raise an error if the request was not successful

        # Parse the CSV data
        data = []
        lines = response.content.decode('utf-8').splitlines()
        csv_reader = csv.DictReader(lines)

        # Use the current working directory as the output directory
        output_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)

        # Define the output file path
        output_file_path = os.path.join(output_dir, "news.csv")

        # Open the CSV file for writing
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Create a CSV DictWriter
            fieldnames = csv_reader.fieldnames  # Use the original field names from the CSV
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()

            # Iterate over the rows and split by ticker
            for row in csv_reader:
                tickers = row.get("Ticker", "").split(",")  # Use .get() to handle missing keys
                for ticker in tickers:
                    row_copy = row.copy()  # Make a copy of the row
                    row_copy["Ticker"] = ticker.strip()  # Assign the individual ticker
                    writer.writerow(row_copy)  # Write the row for each ticker

        print(f"CSV file saved to {output_file_path}")

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except Exception as err:
        print(f"An error occurred: {err}")  # Handle other possible errors

# Call the function to execute
fetch_and_export_news()
