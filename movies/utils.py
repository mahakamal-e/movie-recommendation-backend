import requests
from django.conf import settings
from .models import Movie


def fetch_and_save_trending_movies():
    url = f"{settings.TMDB_BASE_URL}/trending/movie/week"
    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    movies = response.json()["results"]
    saved_movies = []
    for m in movies:
        movie_obj, created = Movie.objects.update_or_create(
            tmdb_id=m["id"],
            defaults={
                "title": m.get("title"),
                "description": m.get("overview"),
                "poster_path": m.get("poster_path"),
                "release_date": m.get("release_date"),
                "genres": m.get("genre_ids", []),
            }
        )
        saved_movies.append(movie_obj)
    return saved_movies
