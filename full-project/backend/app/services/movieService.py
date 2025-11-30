from typing import List, Dict, Any
from ..schemas.movie import Movie, MovieUpdate, MovieCreate
from ..repos.movieRepo import loadMovies, saveMovies, getNextMovieId


class MovieError(Exception):
    """Base class for all movie-related domain errors."""
    pass


class MovieNotFoundError(MovieError):
    def __init__(self, message: str = "Movie not found"):
        super().__init__(message)



def listMovies() -> List[Movie]:
    """Lists all movies currently stored"""
    return loadMovies()


def createMovie(payload: MovieCreate) -> Movie:
    """
    Creates a new movie by generating a new id and adding it into the movies JSON.

    Returns:
        Newly created Movie model
    """
    movies = loadMovies()

    newMovie = Movie(
        id=getNextMovieId(),
        title=payload.title,
        movieGenres=payload.movieGenres,
        directors=payload.directors,
        mainStars=payload.mainStars,
        description=payload.description,
        datePublished=payload.datePublished,
        duration=payload.duration,
        yearReleased=payload.yearReleased,
    )

    movies.append(newMovie)
    saveMovies(movies)
    return newMovie


def getMovieByFilter(
    genre: str | None = None,
    year: int | None = None,
    director: str | None = None,
    star: str | None = None,
) -> List[Movie]:
    """
    Filters movies based on genre, year, director, and star.

    Returns:
        List of Movie models that match the filters.
    """
    movies = loadMovies()
    filteredMovies: List[Movie] = []

    genreQuery = genre.lower().strip() if genre else None
    directorQuery = director.lower().strip() if director else None
    starQuery = star.lower().strip() if star else None
    yearQuery = str(year) if year is not None else None

    for movie in movies:
        movieYear = str(movie.datePublished)[:4]

        # Genre filter
        if genreQuery:
            loweredGenres = [
                genreItem.lower().strip() for genreItem in movie.movieGenres
            ]
            if not any(genreQuery in loweredGenre for loweredGenre in loweredGenres):
                continue

        # Year filter
        if yearQuery:
            startYear = int(yearQuery)
            endYear = startYear + 10
            if not (startYear <= int(movieYear) < endYear):
                continue

        # Director filter
        if directorQuery:
            loweredDirectors = [
                directorItem.lower().strip() for directorItem in movie.directors
            ]
            if not any(
                directorQuery in loweredDirector for loweredDirector in loweredDirectors
            ):
                continue

        # Star filter
        if starQuery:
            loweredStars = [starItem.lower().strip() for starItem in movie.mainStars]
            if not any(starQuery in loweredStar for loweredStar in loweredStars):
                continue

        filteredMovies.append(movie)

    return filteredMovies


def getMovieById(movieId: int | str) -> Movie:
    """
    Retrieves a movie by its ID.

    """
    movieId = int(movieId)
    movies = loadMovies()

    for movie in movies:
        if movie.id == movieId:
            return movie

    raise MovieNotFoundError()


def updateMovie(movieId: int, payload: MovieUpdate) -> Movie:
    """
    Updates a movie by its ID with the provided fields.

    """
    movies = loadMovies()
    updateFields = payload.model_dump(exclude_unset=True)

    for movieIndex, movie in enumerate(movies):
        if movie.id == movieId:
            updatedMovie = movie.model_copy(update=updateFields)
            movies[movieIndex] = updatedMovie
            saveMovies(movies)
            return updatedMovie

    raise MovieNotFoundError()


def deleteMovie(movieId: int) -> None:
    """
    Deletes a movie by its ID.

    """
    movies = loadMovies()
    deleted = False
    result = []

    for movie in movies:
        if int(movie.id) == int(movieId):
            deleted = True
            continue
        result.append(movie)

    if not deleted:
        raise MovieNotFoundError()

    saveMovies(result)


def searchViaFilters(filters: Dict[str, Any]) -> List[Movie]:
    """
    Generic filter function based on keys in the Movie model.
    Applies dynamic filters against each movie converted to a dict.
    """
    movies = loadMovies()
    matchedMovies: List[Movie] = []

    for movie in movies:
        movieDict = movie.model_dump()
        isMatch = True

        for filterKey, filterValue in filters.items():
            if filterKey not in movieDict:
                isMatch = False
                break

            movieFieldValue = movieDict[filterKey]

            if isinstance(filterValue, str):
                if str(movieFieldValue).lower() != filterValue.lower():
                    isMatch = False
                    break

            elif isinstance(filterValue, (int, float)):
                if movieFieldValue != filterValue:
                    isMatch = False
                    break

            elif isinstance(filterValue, list):
                if not all(filterItem in movieFieldValue for filterItem in filterValue):
                    isMatch = False
                    break

        if isMatch:
            matchedMovies.append(movie)

    return matchedMovies


def searchMovie(query: str) -> List[Movie]:
    """
    Searches movies based on a query string across multiple fields.

    Returns:
        List of Movie models that match the search query.
    """
    cleanedQuery = (query or "").lower().strip()
    if not cleanedQuery:
        return []

    movies = loadMovies()
    matchedMovies: List[Movie] = []

    for movie in movies:
        titleText = (movie.title or "").lower()
        descriptionText = (movie.description or "").lower()

        genreText = " ".join(genre.lower() for genre in movie.movieGenres)
        starText = " ".join(star.lower() for star in movie.mainStars)
        directorText = " ".join(director.lower() for director in movie.directors)

        if any(
            cleanedQuery in fieldText
            for fieldText in [
                titleText,
                descriptionText,
                genreText,
                starText,
                directorText,
            ]
        ):
            matchedMovies.append(movie)

    return matchedMovies
