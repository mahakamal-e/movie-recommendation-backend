"""Views for the Movie Recommendation Backend.

This module provides API endpoints for:
- Retrieving trending movies (with caching)
- Managing user favorites
- Fetching recommended movies for a user
- Searching movies by title and/or genre with pagination
"""
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from .models import Movie, UserFavorite
from .serializers import (
    MovieSerializer,
    UserFavoriteSerializer,
    UserFavoriteCreateSerializer,
)
from .utils import fetch_and_save_trending_movies
import random


class TrendingMoviesView(APIView):
    """
    GET /movies/trending/

    Retrieve the list of trending movies with pagination.
    Uses Redis cache to improve performance:
    - If cached data is available, return it.
    - Otherwise, fetch from TMDb, save to DB, and cache the result.
    """

    def get(self, request):
        movies_objs = cache.get("trending_movies_objs")
        if not movies_objs:
            movies_objs = fetch_and_save_trending_movies()
            cache.set("trending_movies_objs", movies_objs, timeout=3600)  # cache objects

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(movies_objs, request)
        serializer = MovieSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserFavoritesView(APIView):
    """
    GET /movies/favorites/
    POST /movies/favorites/

    Manage a user's favorite movies.

    - GET: List all favorites for the authenticated user.
    - POST: Add a movie to the user's favorites using its TMDb ID.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return a list of the authenticated user's favorite movies."""
        favorites = UserFavorite.objects.filter(user=request.user)
        serializer = UserFavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserFavoriteCreateSerializer)
    def post(self, request):
        """Add a new favorite movie for the authenticated user."""
        serializer = UserFavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie_id = serializer.validated_data["movie_id"]
        movie = Movie.objects.get(tmdb_id=movie_id)

        favorite, _ = UserFavorite.objects.get_or_create(
            user=request.user,
            movie=movie,
        )
        result_serializer = UserFavoriteSerializer(favorite)
        return Response(result_serializer.data, status=201)


class RecommendedMoviesView(APIView):
    """
    GET /movies/recommended/

    Return a paginated list of recommended movies for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"recommended_movies_user_{user.id}"
        movies_objs = cache.get(cache_key)

        if movies_objs is None:
            favorite_movies = Movie.objects.filter(userfavorite__user=user)
            favorite_genres = set()
            for movie in favorite_movies:
                favorite_genres.update(movie.genres or [])

            if favorite_genres:  
                # عنده مفضلات → رشحله بناءً على الجانرا
                all_movies = Movie.objects.all()
                recommended = [
                    m for m in all_movies
                    if set(m.genres or []) & favorite_genres
                ]
                recommended.sort(
                    key=lambda m: len(set(m.genres or []) & favorite_genres),
                    reverse=True,
                )
                movies_objs = recommended
            else:
                # مفيش مفضلات → هات تريندينج وخد ٥ عشوائي
                trending = cache.get("trending_movies_objs")
                if not trending:
                    trending = fetch_and_save_trending_movies()
                    cache.set("trending_movies_objs", trending, timeout=3600)

                movies_objs = random.sample(trending, min(5, len(trending)))

            cache.set(cache_key, movies_objs, timeout=3600)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(movies_objs, request)
        serializer = MovieSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SearchMoviesView(APIView):
    """
    GET /movies/search/?q=<title>&genre=<id>

    Search for movies by title and/or genre.
    - `q`: Search by movie title (case-insensitive).
    - `genre`: Filter by genre ID (integer).
    Supports pagination (10 results per page).
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="Search by movie title (case-insensitive).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "genre",
                openapi.IN_QUERY,
                description="Filter by genre ID (integer).",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request):
        """Return a paginated list of movies filtered by title or genre."""
        query = request.GET.get("q", "").strip()
        genre = request.GET.get("genre")

        movies_qs = Movie.objects.all()

        if query:
            movies_qs = movies_qs.filter(title__icontains=query)

        if genre:
            try:
                genre_id = int(genre)
                movies_qs = movies_qs.filter(genres__contains=[genre_id])
            except ValueError:
                return Response({"error": "Genre must be a number"}, status=400)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(movies_qs, request)

        serializer = MovieSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class RemoveFavoriteMovieView(APIView):
    """
    DELETE /movies/favorites/<int:movie_id>/

    Remove a movie from the user's favorites using its TMDb ID.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, movie_id):
        user = request.user
        try:
            favorite = UserFavorite.objects.get(user=user, movie__tmdb_id=movie_id)
            favorite.delete()
            return Response(
                {"detail": "Movie removed from favorites."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except UserFavorite.DoesNotExist:
            return Response(
                {"detail": "Movie not found in favorites."},
                status=status.HTTP_404_NOT_FOUND,
            )