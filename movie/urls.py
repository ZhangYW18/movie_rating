from django.urls import path

from . import movie

urlpatterns = [
    path("load/", movie.load_csv_data, name="load csv data"),
    path("<int:movie_id>/rate/", movie.handle_rate, name="rate a movie"),
    path("evaluate/mid/<int:max_movie_id>/", movie.handle_evaluate_by_movie),
    path("evaluate/uid/<int:max_user_id>/", movie.handle_evaluate_by_user),
    path("<int:id>/", movie.get_movie, name="get movie details"),
    path("rating_distribution/", movie.get_movie_rating_dist, name="get movie rating distribution")
]

