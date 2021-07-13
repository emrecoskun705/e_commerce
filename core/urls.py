from django.urls import path
from .views import (
    homeView
)

app_name = 'core'

urlpatterns = [
    path('', homeView, name='home'),
]