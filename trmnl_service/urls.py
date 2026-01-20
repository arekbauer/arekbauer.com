from django.urls import path
from .views import vct_ticker_view

urlpatterns = [
    path('vct-ticker/', vct_ticker_view, name='trmnl_vct_ticker'),
]