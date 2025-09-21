from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema

from .models import Movie, UserFavorite
from .serializers import MovieSerializer, UserFavoriteSerializer, UserFavoriteCreateSerializer
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

    @swagger_auto_schema(request_body=UserFavoriteCreateSerializer)
    def post(self, request):
        serializer = UserFavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movie_id = serializer.validated_data["movie_id"]
        movie = Movie.objects.get(tmdb_id=movie_id)
        fav, created = UserFavorite.objects.get_or_create(user=request.user, movie=movie)
        result_serializer = UserFavoriteSerializer(fav)  # response كامل
        return Response(result_serializer.data, status=201)
