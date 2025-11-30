import requests
import os
from dotenv import load_dotenv
from .tmdbSchema import TMDbMovie, TMDbRecommendation

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"



def getMovieDetailsByName(movieName: str) -> TMDbMovie | None:
    """Retrieve main movie details from TMDb by searching name."""
    
    response = requests.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": movieName}
    )
    data = response.json()

    if not data.get("results"):
        return None

    movie = data["results"][0]

    return TMDbMovie(
        id=movie["id"],
        title=movie["title"],
        poster=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                if movie.get("poster_path") else None,
        overview=movie.get("overview"),
        rating=movie.get("vote_average"),
    )



def getMovieDetailsById(tmdbId: int) -> TMDbMovie | None:
    response = requests.get(
        f"{BASE_URL}/movie/{tmdbId}",
        params={"api_key": TMDB_API_KEY}
    )
    data = response.json()

    if data.get("status_code"):
        print("TMDB ERROR:", data)
        return None

    return TMDbMovie(
        id=data["id"],
        title=data["title"],
        poster=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
               if data.get("poster_path") else None,
        overview=data.get("overview"),
        rating=data.get("vote_average"),
    )


def getRecommendationsByName(movieName: str) -> list[TMDbRecommendation]:
    """Search movie by name first, then fetch recommendations using its TMDb ID."""
    
    search = requests.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": movieName}
    )
    searchData = search.json()

    if not searchData.get("results"):
        return []

    tmdbId = searchData["results"][0]["id"]

    receivedResponse = requests.get(
        f"{BASE_URL}/movie/{tmdbId}/recommendations",
        params={"api_key": TMDB_API_KEY}
    )
    receivedData = receivedResponse.json()

    results = receivedData.get("results", [])

    return [
        TMDbRecommendation(
            id=m["id"],
            title=m["title"],
            poster=f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                   if m.get("poster_path") else None,
            rating=m.get("vote_average"),
        )
        for m in results[:5]
    ]

def getRecommendationsById(tmdbId: int) -> list[TMDbRecommendation]:
    receivedResponse = requests.get(
        f"{BASE_URL}/movie/{tmdbId}/recommendations",
        params={"api_key": TMDB_API_KEY}
    )
    receivedData = receivedResponse.json()

    results = receivedData.get("results", [])

    return [
        TMDbRecommendation(
            id=m["id"],
            title=m["title"],
            poster=f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
                   if m.get("poster_path") else None,
            rating=m.get("vote_average"),
        )
        for m in results[:5]
    ]
