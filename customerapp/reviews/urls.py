from django.urls import path
from .views import home  # Import the home function from views.py

urlpatterns = [
    path('', home, name='home'),  # The default route loads the homepage
]
