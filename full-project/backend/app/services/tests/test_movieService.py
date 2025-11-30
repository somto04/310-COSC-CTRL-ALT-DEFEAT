from decimal import Decimal
from datetime import date

import pytest

from app.schemas.movie import Movie, MovieCreate, MovieUpdate
from app.services.movieService import (
    MovieNotFoundError,
    listMovies,
    createMovie,
    getMovieByFilter,
    getMovieById,
    updateMovie,
    deleteMovie,
    searchViaFilters,
    searchMovie,
)
import app.services.movieService as movieServiceModule


@pytest.fixture
def sampleMovieList():
    return [
        Movie(
            id=1,
            title="Avengers Endgame",
            movieIMDbRating=Decimal("8.4"),
            movieGenres=["Action", "Adventure"],
            directors=["Russo Brothers"],
            mainStars=["Robert Downey Jr."],
            description="Epic finale of Marvel saga.",
            datePublished=date(2019, 4, 26),
            duration=181,
            yearReleased=2019,
        ),
        Movie(
            id=2,
            title="Inception",
            movieIMDbRating=Decimal("8.8"),
            movieGenres=["Sci-Fi", "Thriller"],
            directors=["Christopher Nolan"],
            mainStars=["Leonardo DiCaprio"],
            description="Dream within a dream.",
            datePublished=date(2010, 7, 16),
            duration=148,
            yearReleased=2010,
        ),
    ]


def testListMoviesReturnsMoviesFromRepo(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = listMovies()

    assert resultMovies is sampleMovieList
    assert len(resultMovies) == 2
    assert resultMovies[0].title == "Avengers Endgame"


def testCreateMovieAddsMovieAndUsesNextId(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return list(sampleMovieList)

    savedMovies = []

    def fakeSaveMovies(movies):
        savedMovies.clear()
        savedMovies.extend(movies)

    def fakeGetNextMovieId():
        return 3

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)
    monkeypatch.setattr(movieServiceModule, "saveMovies", fakeSaveMovies)
    monkeypatch.setattr(movieServiceModule, "getNextMovieId", fakeGetNextMovieId)

    payload = MovieCreate(
        tmdbId=789012,
        title="Testing Movie",
        movieGenres=["Action", "Test"],
        directors=["Test Director"],
        mainStars=["Test Star"],
        description="Just a test movie.",
        datePublished=date(2024, 1, 1),
        duration=120,
        yearReleased=2024,
    )

    newMovie = createMovie(payload)

    assert newMovie.id == 3
    assert newMovie.title == "Testing Movie"
    assert newMovie.datePublished == date(2024, 1, 1)
    assert len(savedMovies) == 3
    assert any(movieItem.id == 3 for movieItem in savedMovies)


def testGetMovieByIdReturnsMovie(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovie = getMovieById(2)

    assert isinstance(resultMovie, Movie)
    assert resultMovie.id == 2
    assert resultMovie.title == "Inception"


def testGetMovieByIdRaisesWhenNotFound(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    with pytest.raises(MovieNotFoundError) as errorInfo:
        getMovieById(999)

    assert "Movie not found" in str(errorInfo.value)


def testUpdateMovieUpdatesFieldsAndSaves(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return list(sampleMovieList)

    savedMovies = []

    def fakeSaveMovies(movies):
        savedMovies.clear()
        savedMovies.extend(movies)

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)
    monkeypatch.setattr(movieServiceModule, "saveMovies", fakeSaveMovies)

    payload = MovieUpdate(title="Updated Title", duration=190)

    updatedMovie = updateMovie(1, payload)

    assert updatedMovie.id == 1
    assert updatedMovie.title == "Updated Title"
    assert updatedMovie.duration == 190
    assert len(savedMovies) == 2
    assert savedMovies[0].title == "Updated Title"
    assert savedMovies[0].duration == 190


def testUpdateMovieRaisesWhenNotFound(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return list(sampleMovieList)

    savedMovies = []

    def fakeSaveMovies(movies):
        savedMovies.clear()
        savedMovies.extend(movies)

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)
    monkeypatch.setattr(movieServiceModule, "saveMovies", fakeSaveMovies)

    payload = MovieUpdate(title="Should Not Save")

    with pytest.raises(MovieNotFoundError) as errorInfo:
        updateMovie(999, payload)

    assert "Movie not found" in str(errorInfo.value)
    assert savedMovies == []


def testDeleteMovieRemovesMovieAndSaves(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return list(sampleMovieList)

    savedMovies = []

    def fakeSaveMovies(movies):
        savedMovies.clear()
        savedMovies.extend(movies)

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)
    monkeypatch.setattr(movieServiceModule, "saveMovies", fakeSaveMovies)

    deleteMovie(1)

    savedIds = [movieItem.id for movieItem in savedMovies]
    assert savedIds == [2]


def testDeleteMovieRaisesWhenNotFound(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return list(sampleMovieList)

    savedMovies = []

    def fakeSaveMovies(movies):
        savedMovies.clear()
        savedMovies.extend(movies)

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)
    monkeypatch.setattr(movieServiceModule, "saveMovies", fakeSaveMovies)

    with pytest.raises(MovieNotFoundError) as errorInfo:
        deleteMovie(999)

    assert "Movie not found" in str(errorInfo.value)
    assert savedMovies == []


# ---------- getMovieByFilter ----------


def testGetMovieByFilterFiltersByGenre(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter(genre="Action")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Avengers Endgame"


def testGetMovieByFilterFiltersByYear(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter(year=2010) # function now users decade

    assert len(resultMovies) == 2
    assert resultMovies[1].title == "Inception"
    assert resultMovies[0].title == "Avengers Endgame"


def testGetMovieByFilterFiltersByDirector(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter(director="Nolan")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testGetMovieByFilterFiltersByStar(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter(star="Robert")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Avengers Endgame"


def testGetMovieByFilterNoFiltersReturnsAll(monkeypatch, sampleMovieList):
    """Covers branch where all filter params are None."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter()

    assert len(resultMovies) == 2
    titles = {movie.title for movie in resultMovies}
    assert titles == {"Avengers Endgame", "Inception"}


def testGetMovieByFilterReturnsEmptyWhenNoMatch(monkeypatch, sampleMovieList):
    """Covers the case where filters produce no results."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = getMovieByFilter(genre="Comedy")

    assert resultMovies == []


# ---------- searchViaFilters ----------


def testSearchViaFiltersMatchesStringAndList(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    filters = {
        "title": "Inception",
        "movieGenres": ["Sci-Fi"],
    }

    resultMovies = searchViaFilters(filters)

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchViaFiltersReturnsEmptyWhenNoMatch(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    filters = {"title": "Nonexistent"}

    resultMovies = searchViaFilters(filters)

    assert resultMovies == []


def testSearchViaFiltersSupportsNumericField(monkeypatch, sampleMovieList):
    """Covers the int/float filter branch."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    filters = {"duration": 148}  # Inception

    resultMovies = searchViaFilters(filters)

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchViaFiltersReturnsEmptyWhenKeyMissing(monkeypatch, sampleMovieList):
    """Covers the branch where filterKey is not in movieDict."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    filters = {"nonexistentField": "whatever"}

    resultMovies = searchViaFilters(filters)

    assert resultMovies == []


# ---------- searchMovie ----------


def testSearchMovieFindsByTitle(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("Inception")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchMovieFindsByDescription(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("Marvel saga")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Avengers Endgame"


def testSearchMovieFindsByGenre(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("thriller")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchMovieFindsByDirector(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("Nolan")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchMovieFindsByStar(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("Leonardo")

    assert len(resultMovies) == 1
    assert resultMovies[0].title == "Inception"


def testSearchMovieReturnsEmptyWhenNoMatch(monkeypatch, sampleMovieList):
    """Non-blank query that finds nothing."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("Some Random Trash")

    assert resultMovies == []


def testSearchMovieReturnsEmptyForBlankQuery(monkeypatch, sampleMovieList):
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    resultMovies = searchMovie("   ")

    assert resultMovies == []

def testSearchViaFiltersNumericFilterNoMatch(monkeypatch, sampleMovieList):
    """Covers the numeric != branch (isMatch = False for int/float)."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    # No movie has duration 999
    filters = {"duration": 999}

    resultMovies = searchViaFilters(filters)

    assert resultMovies == []


def testSearchViaFiltersListFilterNoMatch(monkeypatch, sampleMovieList):
    """Covers the list branch where not all filter items are present."""
    def fakeLoadMovies():
        return sampleMovieList

    monkeypatch.setattr(movieServiceModule, "loadMovies", fakeLoadMovies)

    # No movie has genre "Romance"
    filters = {"movieGenres": ["Romance"]}

    resultMovies = searchViaFilters(filters)

    assert resultMovies == []
