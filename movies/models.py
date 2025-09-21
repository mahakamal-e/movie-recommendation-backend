"""Database models for movies and user favorites."""

import uuid
from django.db import models
from users.models import User


class Movie(models.Model):
    """
    Represents a movie fetched from TMDb or added manually.

    Attributes:
        id (UUID): Primary key for the movie.
        tmdb_id (int): Unique TMDb identifier.
        title (str): Movie title.
        description (str): Plot overview or description.
        genres (list[int]): List of genre IDs (stored as JSON).
        release_date (date): Movie release date (optional).
        poster_path (str): Path or URL to the movie poster.
        created_at (datetime): Auto-generated creation timestamp.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    genres = models.JSONField(default=list)
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the movie title as its string representation."""
        return self.title


class UserFavorite(models.Model):
    """
    Represents a link between a user and one of their favorite movies.

    Attributes:
        id (UUID): Primary key for the record.
        user (User): The user who marked the movie as favorite.
        movie (Movie): The favorite movie.
        created_at (datetime): Auto-generated creation timestamp.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        verbose_name = "User Favorite"
        verbose_name_plural = "User Favorites"

    def __str__(self) -> str:
        """Return a readable string for the favorite entry."""
        return f"{self.user} → {self.movie}"
