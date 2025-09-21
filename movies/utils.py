"""Utility functions for fetching and saving trending movies from TMDb."""

import logging
import requests
from django.conf import settings
from .models import Movie
import time

logger = logging.getLogger(__name__)


def fetch_and_save_trending_movies(max_retries=3, delay=2):
    """
    Fetch trending movies from the TMDb API and save/update them in the database.

    Args:
        max_retries (int): Number of retry attempts if the request fails.
        delay (int): Delay in seconds between retries.

    Returns:
        list[Movie] or dict: List of Movie objects saved/updated or error dict.

    Notes:
        - Uses `update_or_create` to avoid duplicate entries.
        - Handles request exceptions gracefully.
    """
    url = f"{settings.TMDB_BASE_URL}/trending/movie/week"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            break  # success
        except requests.RequestException as exc:
            logger.error("Attempt %s: Failed to fetch trending movies: %s", attempt, exc)
            if attempt < max_retries:
                logger.info("Retrying in %s seconds...", delay)
                time.sleep(delay)
            else:
                return {"error": "Failed to fetch trending movies, please try again later."}

    movies_data = response.json().get("results", [])
    if not movies_data:
        logger.warning("No trending movies found from TMDb API")
        return []

    saved_movies = []
    for movie_data in movies_data:
        try:
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
        except Exception as e:
            logger.error("Failed to save movie %s: %s", movie_data.get("title"), e)
            continue  # skip this movie but keep processing others

    return saved_movies
