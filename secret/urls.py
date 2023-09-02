from django.urls import path
from secret.apps import SecretConfig
from secret.views import SecretCreateView, SecretDeleteView

app_name = SecretConfig.name

urlpatterns = [
    path('generate/', SecretCreateView.as_view(), name='create'),
    path('secrets/<pk>/', SecretDeleteView.as_view(), name='delete'),
]
