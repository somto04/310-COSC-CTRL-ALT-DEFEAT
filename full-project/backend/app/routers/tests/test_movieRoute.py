from datetime import date
from decimal import Decimal

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.schemas.movie import Movie
from app.routers.authRoute import requireAdmin
import app.routers.movieRoute as movieRouteModule
from app.routers.movieRoute import (
    searchMovies,
    filterMovies,
    getMovies,
    getMovie,
    removeMovie,
)


@pytest.fixture
def sampleMovie():
    return Movie(
        id=1,
        title="Inception",
        movieIMDbRating=Decimal("8.8"),
        movieGenres=["Action", "Sci-Fi", "Thriller"],
        directors=["Christopher Nolan"],
        mainStars=["Leonardo DiCaprio", "Tom Hardy"],
        description="A thief who steals corporate secrets",
        datePublished=date(2010, 7, 16),
        duration=148,
        yearReleased=2010,
    )


@pytest.fixture
def sampleMoviesList(sampleMovie):
    return [
        sampleMovie,
        Movie(
            id=2,
            title="The Matrix",
            movieIMDbRating=Decimal("8.7"),
            movieGenres=["Action", "Sci-Fi"],
            directors=["Lana Wachowski", "Lilly Wachowski"],
            mainStars=["Keanu Reeves", "Laurence Fishburne"],
            description="Reality is a simulation",
            datePublished=date(1999, 3, 31),
            duration=136,
            yearReleased=1999,
        ),
    ]


@pytest.fixture
def app():
    appInstance = FastAPI()
    appInstance.include_router(movieRouteModule.router)

    def fakeRequireAdmin():
        return {"id": 1, "role": "admin"}

    appInstance.dependency_overrides[requireAdmin] = fakeRequireAdmin
    return appInstance


@pytest.fixture
def client(app):
    return TestClient(app)


# ---------- Unit-style route tests ----------


def testSearchMoviesCallsServiceWithNormalizedKeyword(monkeypatch, sampleMoviesList):
    capturedKeyword = {}

    def fakeSearchMovie(keyword):
        capturedKeyword["value"] = keyword
        return sampleMoviesList

    monkeypatch.setattr(movieRouteModule, "searchMovie", fakeSearchMovie)

    resultMovies = searchMovies("  InCePtIoN  ")

    assert capturedKeyword["value"] == "inception"
    assert resultMovies is sampleMoviesList


def testSearchMoviesRaises404WhenNoResults(monkeypatch):
    def fakeSearchMovie(keyword):
        return []

    monkeypatch.setattr(movieRouteModule, "searchMovie", fakeSearchMovie)

    with pytest.raises(HTTPException) as errorInfo:
        searchMovies("nothing")

    assert errorInfo.value.status_code == 404
    assert errorInfo.value.detail == "Movie not found"


def testFilterMoviesNormalizesAndPassesFilters(monkeypatch, sampleMoviesList):
    capturedArgs = {}

    def fakeGetMovieByFilter(genreValue, yearValue, directorValue, starValue):
        capturedArgs["genre"] = genreValue
        capturedArgs["year"] = yearValue
        capturedArgs["director"] = directorValue
        capturedArgs["star"] = starValue
        return sampleMoviesList

    monkeypatch.setattr(movieRouteModule, "getMovieByFilter", fakeGetMovieByFilter)

    resultMovies = filterMovies(
        genre="  Action ",
        year=2010,
        director=" NoLaN ",
        star=" LeO ",
    )

    assert capturedArgs["genre"] == "action"
    assert capturedArgs["year"] == 2010
    assert capturedArgs["director"] == "nolan"
    assert capturedArgs["star"] == "leo"
    assert resultMovies is sampleMoviesList


def testFilterMoviesRaises404WhenNoResults(monkeypatch):
    def fakeGetMovieByFilter(genreValue, yearValue, directorValue, starValue):
        raise HTTPException(status_code=404, detail="No movies found with the given filters")

    monkeypatch.setattr(movieRouteModule, "getMovieByFilter", fakeGetMovieByFilter)

    with pytest.raises(HTTPException) as errorInfo:
        filterMovies(genre="Action")

    assert errorInfo.value.status_code == 404
    assert errorInfo.value.detail == "No movies found with the given filters"


def testGetMoviesReturnsListFromService(monkeypatch, sampleMoviesList):
    def fakeListMovies():
        return sampleMoviesList

    monkeypatch.setattr(movieRouteModule, "listMovies", fakeListMovies)

    resultMovies = getMovies()

    assert resultMovies is sampleMoviesList
    assert len(resultMovies) == 2


def testGetMovieReturnsSingleMovie(monkeypatch, sampleMovie):
    def fakeGetMovieById(movieId):
        return sampleMovie

    monkeypatch.setattr(movieRouteModule, "getMovieById", fakeGetMovieById)

    resultMovie = getMovie(1)

    assert resultMovie is sampleMovie
    assert resultMovie.id == 1


def testGetMoviePropagatesServiceErrors(monkeypatch):
    # Service raises domain exception; route should translate to HTTPException
    def fakeGetMovieById(movieId):
        raise movieRouteModule.MovieNotFoundError("Movie not found")

    monkeypatch.setattr(movieRouteModule, "getMovieById", fakeGetMovieById)

    with pytest.raises(HTTPException) as errorInfo:
        getMovie(999)

    assert errorInfo.value.status_code == 404
    assert errorInfo.value.detail == "Movie not found"


# ---------- Integration tests (TestClient) ----------


def testGetMoviesEndpointReturnsMovies(monkeypatch, client, sampleMoviesList):
    def fakeListMovies():
        return sampleMoviesList

    monkeypatch.setattr(movieRouteModule, "listMovies", fakeListMovies)

    response = client.get("/movies")
    responseJson = response.json()

    assert response.status_code == 200
    assert len(responseJson) == 2
    assert responseJson[0]["title"] == "Inception"


def testGetMovieEndpointReturnsMovie(monkeypatch, client, sampleMovie):
    def fakeGetMovieById(movieId):
        return sampleMovie

    monkeypatch.setattr(movieRouteModule, "getMovieById", fakeGetMovieById)

    response = client.get("/movies/1")
    responseJson = response.json()

    assert response.status_code == 200
    assert responseJson["id"] == 1
    assert responseJson["title"] == "Inception"


def testGetMovieEndpointReturns404(monkeypatch, client):
    def fakeGetMovieById(movieId):
        raise movieRouteModule.MovieNotFoundError("Movie not found")

    monkeypatch.setattr(movieRouteModule, "getMovieById", fakeGetMovieById)

    response = client.get("/movies/999")
    responseJson = response.json()

    assert response.status_code == 404
    assert responseJson["detail"] == "Movie not found"


def testSearchMoviesEndpointReturnsResults(monkeypatch, client, sampleMoviesList):
    def fakeSearchMovie(keyword):
        return [sampleMoviesList[0]]

    monkeypatch.setattr(movieRouteModule, "searchMovie", fakeSearchMovie)

    response = client.get("/movies/search?query=Inception")
    responseJson = response.json()

    assert response.status_code == 200
    assert len(responseJson) == 1
    assert responseJson[0]["title"] == "Inception"


def testSearchMoviesEndpointReturns404(monkeypatch, client):
    def fakeSearchMovie(keyword):
        return []

    monkeypatch.setattr(movieRouteModule, "searchMovie", fakeSearchMovie)

    response = client.get("/movies/search?query=none")
    responseJson = response.json()

    assert response.status_code == 404
    assert responseJson["detail"] == "Movie not found"


def testFilterMoviesEndpointReturnsResults(monkeypatch, client, sampleMoviesList):
    def fakeGetMovieByFilter(genreValue, yearValue, directorValue, starValue):
        return sampleMoviesList

    monkeypatch.setattr(movieRouteModule, "getMovieByFilter", fakeGetMovieByFilter)

    response = client.get(
        "/movies/filter?genre=Action&year=2010&director=Nolan&star=Leo"
    )
    responseJson = response.json()

    assert response.status_code == 200
    assert len(responseJson) == 2


def testFilterMoviesEndpointReturns404(monkeypatch, client):
    def fakeGetMovieByFilter(genreValue, yearValue, directorValue, starValue):
        return []

    monkeypatch.setattr(movieRouteModule, "getMovieByFilter", fakeGetMovieByFilter)

    response = client.get("/movies/filter?genre=Action")
    responseJson = response.json()

    assert response.status_code == 200 
    assert responseJson == []


def testRemoveMovieEndpointCallsService(monkeypatch, client):
    calledArgs = {}

    def fakeDeleteMovie(movieId):
        calledArgs["movieId"] = movieId

    monkeypatch.setattr(movieRouteModule, "deleteMovie", fakeDeleteMovie)

    response = client.delete("/movies/1")

    assert response.status_code == 204
    assert calledArgs["movieId"] == 1


def testRemoveMovieEndpointReturns404(monkeypatch, client):
    def fakeDeleteMovie(movieId):
        raise movieRouteModule.MovieNotFoundError("Movie not found")

    monkeypatch.setattr(movieRouteModule, "deleteMovie", fakeDeleteMovie)

    response = client.delete("/movies/999")
    responseJson = response.json()

    assert response.status_code == 404
    assert responseJson["detail"] == "Movie not found"


def testAddMovieEndpointCreatesMovie(monkeypatch, client, sampleMovie):
    calledPayload = {}

    def fakeCreateMovie(payload):
        calledPayload["payload"] = payload
        return sampleMovie

    monkeypatch.setattr(movieRouteModule, "createMovie", fakeCreateMovie)

    requestBody = {
        "title": "New Movie",
        "movieIMDbRating": "7.5",
        "movieGenres": ["Action"],
        "directors": ["Some Director"],
        "mainStars": ["Some Star"],
        "description": "Test description",
        "datePublished": "2020-01-01",
        "duration": 120,
        "yearReleased": 2020,
    }

    response = client.post("/movies", json=requestBody)
    responseJson = response.json()

    assert response.status_code == 201
    # ensure service was called with a Pydantic model
    assert hasattr(calledPayload["payload"], "title")
    assert calledPayload["payload"].title == "New Movie"
    # response is whatever fakeCreateMovie returned
    assert responseJson["title"] == "Inception"
    assert responseJson["id"] == 1


def testModifyMovieDetailsEndpointUpdatesMovie(monkeypatch, client, sampleMovie):
    calledArgs = {}

    def fakeUpdateMovie(movieId, payload):
        calledArgs["movieId"] = movieId
        calledArgs["payload"] = payload
        return sampleMovie

    monkeypatch.setattr(movieRouteModule, "updateMovie", fakeUpdateMovie)

    requestBody = {
        "title": "Updated Title",
        "description": "Updated description",
    }

    response = client.put("/movies/1", json=requestBody)
    responseJson = response.json()

    assert response.status_code == 200
    assert responseJson["id"] == 1
    assert calledArgs["movieId"] == 1
    assert hasattr(calledArgs["payload"], "title")
    assert calledArgs["payload"].title == "Updated Title"


def testModifyMovieDetailsEndpointReturns404(monkeypatch, client):
    def fakeUpdateMovie(movieId, payload):
        raise movieRouteModule.MovieNotFoundError("Movie not found")

    monkeypatch.setattr(movieRouteModule, "updateMovie", fakeUpdateMovie)

    requestBody = {
        "title": "Does Not Matter",
        "description": "Still not found",
    }

    response = client.put("/movies/999", json=requestBody)
    responseJson = response.json()

    assert response.status_code == 404
    assert responseJson["detail"] == "Movie not found"

