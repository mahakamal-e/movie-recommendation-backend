"""Serializers for the Movie Recommendation Backend.

This module provides:
- MovieSerializer: For displaying movie details (with genre names).
- UserFavoriteSerializer: For listing user favorites with nested movie data.
- UserFavoriteCreateSerializer: For adding a movie to a user's favorites.
"""

from rest_framework import serializers
from .models import Movie, UserFavorite

# Mapping of TMDb genre IDs to human-readable names
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Sci-Fi",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}


class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for the Movie model.

    Includes an extra field `genre_names` that converts
    numeric genre IDs into their human-readable names.
    """

    genre_names = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "description",
            "poster_path",
            "release_date",
            "genres",
            "genre_names",
        ]

    def get_genre_names(self, obj):
        """Return a list of genre names for the given movie."""
        return [GENRE_MAP.get(g, "Unknown") for g in (obj.genres or [])]


class UserFavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserFavorite model.

    Provides:
    - The related movie details (nested MovieSerializer).
    - The user as a string (using `__str__`).
    """

    movie = MovieSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ["id", "user", "movie"]


class UserFavoriteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new UserFavorite.

    Accepts only the movie's TMDb ID as `movie_id`.
    """

    movie_id = serializers.IntegerField()

    class Meta:
        model = UserFavorite
        fields = ["movie_id"]
