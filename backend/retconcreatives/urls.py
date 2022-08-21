from django.urls import path

from . import views

urlpatterns = [
    path('makeplaceholdereps', views.create_placeholder_episodes, name='create-placeholder'),
]