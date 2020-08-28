from django.urls import path

from . import views

urlpatterns = [
    path('edit_collection', views.edit_collection, name='edit-collection'),
]