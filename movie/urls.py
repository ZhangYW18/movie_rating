from django.urls import path

from . import movie

urlpatterns = [
    path("load/", movie.load_csv_data, name="load csv data"),
    path("<int:id>/", movie.get_movie, name="get movie details"),
    path("rating_distribution/", movie.get_movie_rating_dist, name="get movie rating distribution")
]