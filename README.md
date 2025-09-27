# 🎬 Movie Recommendation Backend

A Django REST API backend for a movie recommendation app, complete with user authentication, favorite movies, trending and recommended movies, search, and caching with Redis.

---

## 🚀 Project Overview

This backend powers a movie recommendation platform where users can:

- Browse trending movies
- Search movies by title or genre
- Save favorite movies
- Get personalized recommendations based on favorite genres
- Secure authentication using JWT

---

## 🛠 Features

### Core Features
- User Authentication (Register, Login, Token Refresh)
- Favorite Movies (Add, Remove, List)
- Trending Movies (Paginated, cached via Redis)
- Recommended Movies (Based on favorite genres or random trending movies)
- Movie Search (By title and/or genre, paginated)

### Bonus Features
- JWT authentication with `rest_framework_simplejwt`
- Swagger API documentation
- Redis caching for trending and recommended movies
- Dockerized setup for easy deployment

### 🔄 Data Flow & TMDb Integration

- Movie data is fetched from The Movie Database (TMDb) API

- When users search, browse trending, or request recommendations:

1. The API fetches movie details from TMDb.

2. Results are stored in the local PostgreSQL database for persistence.

3. Frequently requested data (e.g., trending movies) is cached in Redis for faster responses.

This ensures that users always get fresh movie data with optimized performance.
---

## 📦 Requirements

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

To get the project on your local machine, run:

```bash
git clone https://github.com/mahakamal-e/movie-recommendation-backend.git
cd movie_backend


### 2. Create a `.env` File (Optional)

All required environment variables are already set in the Docker Compose file.  

You only need a `.env` file if you want to override the defaults, for example:

```env
DJANGO_DB_NAME=movie_db
DJANGO_DB_USER=movie_user
DJANGO_DB_PASSWORD=movie_pass
DJANGO_DB_HOST=db
DJANGO_DB_PORT=5432
DJANGO_REDIS_HOST=redis
DJANGO_REDIS_PORT=6379
TMDB_API_KEY=<your_tmdb_api_key>
```
Note: If you don’t create a .env file, Docker Compose will use the default environment variables defined in the docker-compose.yml.

### 3. Build and start Docker containers
```docker compose up --build -d```
-d runs containers in detached mode (background)

This starts Django, PostgreSQL, and Redis

To see logs directly in the terminal instead of running in the background, use:

```docker compose up```

### 4. Run Migrations
```docker compose exec web python manage.py migrate ```


### 5. Create a Superuser
```docker compose exec web python manage.py createsuperuser ```

### 🚀 Access the Application

- **API:** [http://localhost:8000](http://localhost:8000)  
- **Swagger Documentation:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) 
for interactive API docs.

## 🗄 Database & Redis
PostgreSQL is available at db:5432 in Docker. Redis caching is available at redis:6379 for trending and recommended movies.
## 📄 API Documentation

The backend provides interactive and structured API documentation for developers:

- **Swagger** UI (Interactive API Docs)
http://localhost:8000/api/docs/

Allows you to explore and try out API endpoints directly from the browser.

 - **ReDoc** UI (Structured API Docs)
http://localhost:8000/api/redoc/
Provides a clean, organized view of all endpoints for easy reading and reference.
## API Endpoints

### Authentication


| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/token/` | POST | Obtain JWT token |
| `/api/auth/token/refresh/` | POST | Refresh JWT token |
| `/api/users/me/` | GET | Get current user profile |
| `/api/me/change-password/` | POST | Change user password |

### **Authentication Usage Examples**

**Register a new user**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "yourusername",
  "email": "your@email.com",
  "password": "yourpassword"
}
```
**Obtain JWT token**
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "yourusername",
  "password": "yourpassword"
}
```
### Movies

| Endpoint | Method | Description |
|----------|--------|------------|
| `/api/movies/trending/` | GET | List trending movies (paginated) |
| `/api/movies/recommended/` | GET | Recommended movies based on favorite genres or 5 random trending if none |
| `/api/movies/search/` | GET | Search movies by title and/or genre |
| `/api/movies/favorites/` | GET/POST | List/Add user’s favorite movies |
| `/api/movies/favorites/remove/<movie_id>/` | DELETE | Remove a movie from favorites |



## Live Project & Demo
- Live project: [https://your-live-project-link.com](https://your-live-project-link.com)
- Demo video: [https://your-demo-video-link.com](https://your-demo-video-link.com)

## Testing
(Optional) Run tests:
```bash
docker compose exec web python manage.py test




