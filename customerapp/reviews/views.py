import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import io
import urllib, base64
import os
from django.shortcuts import render  # ✅ Make sure this is imported!

# Define the path to the CSV file (adjust as needed)
CSV_FILE_PATH = "/Users/patrickstewart/Documents/Customer review platform/data/product_processed.csv"

def load_data():
    """Load the latest DataFrame from the CSV."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["review_text", "aspect_terms", "sentiments"])  # Empty DataFrame if missing

def home(request):
    df = load_data()

    # Convert DataFrame to a list of dictionaries for template rendering
    reviews = df.to_dict(orient='records')

    # Create Pie Chart for Sentiment Distribution
    if not df.empty and 'sentiments' in df:
        sentiment_counts = df['sentiments'].value_counts()

        plt.figure(figsize=(6, 6))
        sentiment_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colormap='coolwarm')
        plt.title("Sentiment Distribution")

        # Convert the plot to an image
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        string = base64.b64encode(buf.read()).decode("utf-8")
        chart_url = f"data:image/png;base64,{string}"
        plt.close()
    else:
        chart_url = None  # No chart if no data

    return render(request, "reviews/home.html", {"reviews": reviews, "chart_url": chart_url})
