from django.db import models

class Review(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    content = models.TextField()
    sentiment = models.CharField(max_length=8, choices=SENTIMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
