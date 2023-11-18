from django.urls import path

from . import movie

urlpatterns = [
    path("load/", movie.load_csv_data, name="load csv data"),
]