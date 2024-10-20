from flask import Flask, render_template, jsonify, request
import subprocess
import pandas as pd

app = Flask(__name__)

# Run scripts and read data
def run_scripts_and_get_data():
    # Run your scripts to prepare data
    scripts = ['export.py', 'sentiment.py', 'price.py', 'compilesent.py', 'plotone.py']
    for script in scripts:
        subprocess.run(['python', script], capture_output=True)

    # Load the data for plotting
    price_data = pd.read_csv('export.csv')
    sentiment_data = pd.read_csv('average_sentiment_per_ticker.csv')
    
    return price_data, sentiment_data

@app.route('/')
def index():
    price_data, sentiment_data = run_scripts_and_get_data()
    return render_template('graph.html', price_data=price_data.to_json(orient='records'), 
                           sentiment_data=sentiment_data.to_json(orient='records'))

@app.route('/get_data')
def get_data():
    price_data, _ = run_scripts_and_get_data()
    return price_data.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)
