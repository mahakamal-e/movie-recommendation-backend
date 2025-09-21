from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from movies.models import Movie, UserFavorite
from django.urls import reverse

User = get_user_model()


class MovieModelTest(TestCase):
    """Tests for Movie model."""

    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=100,
            title="Test Movie",
            description="Description",
            genres=[28, 12],
            release_date="2025-01-01",
        )

    def test_movie_fields(self):
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertIn(28, self.movie.genres)


class UserFavoriteModelTest(TestCase):
    """Tests for UserFavorite model."""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.movie = Movie.objects.create(tmdb_id=101, title="Movie 101")
        self.favorite = UserFavorite.objects.create(user=self.user, movie=self.movie)

    def test_unique_constraint(self):
        with self.assertRaises(Exception):
            UserFavorite.objects.create(user=self.user, movie=self.movie)


class MovieViewsTest(TestCase):
    """Tests for movie-related API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.movie1 = Movie.objects.create(tmdb_id=1, title="Batman", genres=[28])
        self.movie2 = Movie.objects.create(tmdb_id=2, title="Spiderman", genres=[28])
        self.favorite_url = reverse("user_favorites")
        self.search_url = reverse("movies_search")
        self.trending_url = reverse("movies_trending")
        self.recommended_url = reverse("movies_recommended")

    def test_trending_movies_view(self):
        res = self.client.get(self.trending_url)
        self.assertEqual(res.status_code, 200)
        # Pagination may be used, so check 'results' key
        if "results" in res.json():
            self.assertTrue(len(res.json()["results"]) >= 0)
        else:
            self.assertTrue(len(res.json()) >= 0)

    def test_search_movies_by_title(self):
        res = self.client.get(self.search_url, {"q": "Batman"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.json())
        self.assertEqual(len(res.json()["results"]), 1)

    def test_search_movies_by_genre(self):
        res = self.client.get(self.search_url, {"genre": 28})
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.json())
        self.assertTrue(len(res.json()["results"]) >= 2)

    def test_search_movies_invalid_genre(self):
        res = self.client.get(self.search_url, {"genre": "abc"})
        self.assertEqual(res.status_code, 400)

    def test_userfavorites_requires_auth(self):
        res = self.client.get(self.favorite_url)
        self.assertEqual(res.status_code, 401)

def test_userfavorites_post_authenticated(self):
    """Authenticated user can add a favorite movie."""
    # Authenticate user
    self.client.force_authenticate(user=self.user)

    # تأكدي من وجود الفيلم في DB قبل POST
    if not Movie.objects.filter(tmdb_id=self.movie1.tmdb_id).exists():
        Movie.objects.create(
            tmdb_id=self.movie1.tmdb_id,
            title=self.movie1.title,
            genres=self.movie1.genres or []
        )

    res = self.client.post(self.favorite_url, {"movie_id": self.movie1.tmdb_id})
    self.assertEqual(res.status_code, 201)
    self.assertEqual(UserFavorite.objects.filter(user=self.user).count(), 1)

    def test_recommended_movies_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.recommended_url)
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.json())
