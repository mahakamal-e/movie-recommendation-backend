"""Utility functions for fetching and saving trending movies from TMDb."""

import logging
import requests
from django.conf import settings
from .models import Movie

logger = logging.getLogger(__name__)


def fetch_and_save_trending_movies():
    """
    Fetch trending movies from the TMDb API and save/update them in the database.

    Returns:
        list[Movie]: A list of Movie objects that were saved or updated.

    Notes:
        - Uses `update_or_create` to avoid duplicate entries.
        - Requires the following settings:
            TMDB_BASE_URL (str) – Base URL of the TMDb API.
            TMDB_API_KEY (str) – Your TMDb API key.
    """
    url = f"{settings.TMDB_BASE_URL}/trending/movie/week"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch trending movies from TMDb: %s", exc)
        return []

    movies_data = response.json().get("results", [])
    saved_movies = []

    for movie_data in movies_data:
        movie_obj, _ = Movie.objects.update_or_create(
            tmdb_id=movie_data.get("id"),
            defaults={
                "title": movie_data.get("title", ""),
                "description": movie_data.get("overview", ""),
                "poster_path": movie_data.get("poster_path", ""),
                "release_date": movie_data.get("release_date"),
            },
        )
        saved_movies.append(movie_obj)

    return saved_movies
