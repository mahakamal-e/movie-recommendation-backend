from django.urls import path
from .views import TrendingMoviesView, UserFavoritesView


urlpatterns = [
    path("movies/trending/", TrendingMoviesView.as_view(), name="movies_trending"),
    path("users/favorites/", UserFavoritesView.as_view(), name="user_favorites"),
]