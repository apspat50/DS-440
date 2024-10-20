import pandas as pd
import matplotlib.pyplot as plt

# Path to the CSV files
input_sentiment_csv = "average_sentiment_per_ticker.csv"
input_price_csv = "export.csv"

# Read the CSV file containing average sentiment data
try:
    sentiment_df = pd.read_csv(input_sentiment_csv)
except pd.errors.EmptyDataError:
    print(f"Error: The file {input_sentiment_csv} is empty or cannot be read.")
    exit(1)

# Read the CSV file containing stock price data
try:
    price_df = pd.read_csv(input_price_csv)
except pd.errors.EmptyDataError:
    print(f"Error: The file {input_price_csv} is empty or cannot be read.")
    exit(1)

# Ensure 'Ticker' and 'Change' columns exist in price_df
if 'Ticker' not in price_df.columns or 'Change' not in price_df.columns:
    print(f"Error: The 'Ticker' or 'Change' column is missing in {input_price_csv}.")
    exit(1)

# Clean the 'Change' column: remove percentage signs and convert to numeric
price_df['Change'] = price_df['Change'].str.replace('%', '', regex=False)  # Use regex=False for better performance
price_df['Change'] = pd.to_numeric(price_df['Change'], errors='coerce')  # Convert to numeric, coerce errors to NaN

# Drop any rows in price_df with NaN values in 'Change'
price_df.dropna(subset=['Change'], inplace=True)

# Merge the two DataFrames on 'Ticker' to combine sentiment and price change data
combined_df = pd.merge(sentiment_df, price_df[['Ticker', 'Change']], on='Ticker', how='inner')

# Ensure 'Combined_Sentiment' exists in sentiment_df
if 'Combined_Sentiment' not in combined_df.columns:
    print(f"Error: The 'Combined_Sentiment' column is missing in sentiment data.")
    exit(1)

# Center the 'Combined_Sentiment' and 'Change' columns around 0
combined_df['Combined_Sentiment'] = combined_df['Combined_Sentiment'] - combined_df['Combined_Sentiment'].mean()
combined_df['Change'] = combined_df['Change'] - combined_df['Change'].mean()

# Create a 4-grid plot based on sentiment and change
plt.figure(figsize=(10, 6))

# Define the limits of the quadrants
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)

# Plot the data points
for i, row in combined_df.iterrows():
    plt.scatter(row['Combined_Sentiment'], row['Change'], label=row['Ticker'], s=50)
    plt.text(row['Combined_Sentiment'], row['Change'], row['Ticker'], fontsize=9, ha='right', va='bottom')

# Add labels for the quadrants
plt.text(1, 1, 'Buy', fontsize=12, ha='center', va='center')
plt.text(-1, 1, 'Hold', fontsize=12, ha='center', va='center')
plt.text(-1, -1, 'Sell', fontsize=12, ha='center', va='center')
plt.text(1, -1, 'Hold', fontsize=12, ha='center', va='center')

# Add labels and title
plt.title('Price Change vs Average Sentiment')
plt.xlabel('Average Sentiment')
plt.ylabel('Price Change (%)')
plt.grid(True)

# Set the x and y axis limits to spread out the data across 4 quadrants
plt.xlim(combined_df['Combined_Sentiment'].min() - 1, combined_df['Combined_Sentiment'].max() + 1)
plt.ylim(combined_df['Change'].min() - 1, combined_df['Change'].max() + 1)

# Show the plot
plt.show()
