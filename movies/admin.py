"""
Admin configuration for Movie and UserFavorite models.

This module registers the Movie and UserFavorite models with the Django admin site,
providing an interface to view, filter, and manage movie records and user favorites.
"""

from django.contrib import admin
from .models import Movie, UserFavorite


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Admin view for Movie model.

    Features:
        - Display movie title, TMDb ID, and release date in list view.
        - Searchable by title and TMDb ID.
        - Filterable by release date.
    """
    list_display = ("title", "tmdb_id", "release_date", "created_at")
    search_fields = ("title", "tmdb_id")
    list_filter = ("release_date", "created_at")


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """
    Admin view for UserFavorite model.

    Features:
        - Display user, movie, and creation date in list view.
        - Searchable by user and movie title.
        - Prevents duplicate entries through model constraints.
    """
    list_display = ("user", "movie", "created_at")
    search_fields = ("user__username", "movie__title")
    list_filter = ("created_at",)
