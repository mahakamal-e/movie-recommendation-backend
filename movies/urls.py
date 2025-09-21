from django.urls import path
from .views import TrendingMoviesView, UserFavoritesView, RecommendedMoviesView, SearchMoviesView


urlpatterns = [
    path("movies/trending/", TrendingMoviesView.as_view(), name="movies_trending"),
    path("movies/recommended/", RecommendedMoviesView.as_view(), name="movies_recommended"),
    path("movies/search/", SearchMoviesView.as_view(), name="movies_search"),

    path("users/favorites/", UserFavoritesView.as_view(), name="user_favorites"),
    
]