import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import io
import urllib, base64
import os
from django.shortcuts import render  # ✅ Make sure this is imported!
from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Review
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Define the path to the CSV file (adjust as needed)
CSV_FILE_PATH = "/Users/patrickstewart/Documents/Customer review platform/data/product_processed.csv"

def load_data():
    """Load the latest DataFrame from the CSV."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["review_text", "aspect_terms", "sentiments"])  # Empty DataFrame if missing


def process_csv_view(request):
    file_path = os.path.join(settings.BASE_DIR.parent, 'data', 'aspect_counts.csv')
    df = pd.read_csv(file_path)
    # Process your DataFrame here
    # For example, convert it to a list of dictionaries
    data = df.to_dict('records')
    return render(request, 'your_template.html', {'data': data})


def review_dashboard(request):
    # Load data from CSV
    sentiments_path = os.path.join(settings.BASE_DIR.parent, 'data', 'whole_review_sentiments.csv')
    
    # Read the CSV file
    df = pd.read_csv(sentiments_path)

    # Convert submission_time to datetime
    df['submission_time'] = pd.to_datetime(df['submission_time'])

    # Create a sentiment column based on normalized_sentiment_score
    df['sentiment'] = pd.cut(df['normalized_sentiment_score'], 
                             bins=[-float('inf'), -0.33, 0.33, float('inf')],
                             labels=['negative', 'neutral', 'positive'])

    # Group by month and sentiment
    reviews_by_month = df.groupby([df['submission_time'].dt.to_period('M'), 'sentiment'], observed=True).size().unstack(fill_value=0)
    # Create the graph
    fig = make_subplots(rows=1, cols=1)
    for sentiment in ['positive', 'neutral', 'negative']:
        fig.add_trace(go.Bar(x=reviews_by_month.index.astype(str), 
                             y=reviews_by_month[sentiment], 
                             name=sentiment.capitalize()))

    fig.update_layout(barmode='stack', title='Reviews by Month and Sentiment')
    graph = fig.to_html(full_html=False)

    # Calculate additional statistics
    total_reviews = df.shape[0]
    avg_sentiment = df['normalized_sentiment_score'].mean()
    # Load and process aspect counts
    aspect_counts_path = os.path.join(settings.BASE_DIR.parent, 'data', 'aspect_counts.csv')
    aspect_df = pd.read_csv(aspect_counts_path)
    
    # Calculate aspect scores
    aspect_scores = aspect_df.groupby('normalized_aspects').apply(
        lambda x: (x[x['sentiments'] == 'positive']['Count'].sum() - 
                   x[x['sentiments'] == 'negative']['Count'].sum()) / 
                   x['Count'].sum()
    ).reset_index()
    aspect_scores.columns = ['Aspect', 'Score']
    aspect_scores['Score'] = aspect_scores['Score'].round(2)
    
    # Sort aspects by absolute score value
    aspect_scores = aspect_scores.reindex(aspect_scores['Score'].abs().sort_values(ascending=False).index)
    
    # Convert DataFrame to list of dicts for template rendering
    aspect_table = aspect_scores.to_dict('records')

    context = {
        'graph': graph,
        'total_reviews': total_reviews,
        'avg_sentiment': f"{avg_sentiment:.2f}",
        'aspect_table': aspect_table,
    }
    return render(request, 'reviews/dashboard.html', context)