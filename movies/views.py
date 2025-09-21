from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Movie, UserFavorite
from .serializers import MovieSerializer, UserFavoriteSerializer
from .utils import fetch_and_save_trending_movies


class TrendingMoviesView(APIView):
    def get(self, request):
        movies = cache.get("trending_movies")
        if not movies:
            movies_objs = fetch_and_save_trending_movies()
            serializer = MovieSerializer(movies_objs, many=True)
            movies = serializer.data
            cache.set("trending_movies", movies, timeout=3600)
        return Response(movies)


class UserFavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = UserFavorite.objects.filter(user=request.user)
        serializer = UserFavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        movie_id = request.data.get("movie_id")
        movie = Movie.objects.get(id=movie_id)
        fav, created = UserFavorite.objects.get_or_create(user=request.user, movie=movie)
        serializer = UserFavoriteSerializer(fav)
        return Response(serializer.data)
