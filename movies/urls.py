"""
URL configuration for the movies app.

This module defines the URL patterns for movie-related API endpoints:
    - Trending movies
    - Recommended movies
    - Search movies
    - User favorites management (list, remove)
"""

from django.urls import path
from .views import (
    TrendingMoviesView,
    UserFavoritesView,
    RecommendedMoviesView,
    SearchMoviesView,
    RemoveFavoriteMovieView,
)

urlpatterns = [
    path(
        "movies/trending/",
        TrendingMoviesView.as_view(),
        name="movies_trending",
    ),
    path(
        "movies/recommended/",
        RecommendedMoviesView.as_view(),
        name="movies_recommended",
    ),
    path(
        "movies/search/",
        SearchMoviesView.as_view(),
        name="movies_search",
    ),
    path(
        "users/favorites/",
        UserFavoritesView.as_view(),
        name="user_favorites",
    ),
    path(
        "movies/favorites/remove/<int:movie_id>/",
        RemoveFavoriteMovieView.as_view(),
        name="remove_favorite_movie",
    ),
]
