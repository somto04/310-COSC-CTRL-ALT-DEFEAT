from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.routers.authRoute import requireAdmin
from app.schemas.movie import Movie, MovieCreate, MovieUpdate
from app.services.movieService import (
    MovieNotFoundError,
    listMovies,
    createMovie,
    getMovieById,
    updateMovie,
    deleteMovie,
    searchMovie,
    getMovieByFilter,
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/search", response_model=List[Movie])
def searchMovies(query: Optional[str] = None):
    keyword = (query or "").lower().strip()

    results = searchMovie(keyword)  # returns List[Movie]

    if not results:
        raise HTTPException(status_code=404, detail="Movie not found")

    return results


@router.get("/filter", response_model=List[Movie])
def filterMovies(
    genre: Optional[str] = None,
    year: Optional[int] = None,
    director: Optional[str] = None,
    star: Optional[str] = None,
):

    genreQuery = genre.lower().strip() if genre else None
    directorQuery = director.lower().strip() if director else None
    starQuery = star.lower().strip() if star else None

    results = getMovieByFilter(genreQuery, year, directorQuery, starQuery)

    return results


@router.get("", response_model=List[Movie])
def getMovies():
    return listMovies()


@router.get("/{movieId}", response_model=Movie)
def getMovie(movieId: int):
    try:
        return getMovieById(movieId)
    except MovieNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ADMIN ONLY #


@router.post("", response_model=Movie, status_code=status.HTTP_201_CREATED)
def addMovie(payload: MovieCreate, admin: dict = Depends(requireAdmin)):
    return createMovie(payload)


@router.put("/{movieId}", response_model=Movie)
def modifyMovieDetails(
    movieId: int, payload: MovieUpdate, admin: dict = Depends(requireAdmin)
):
    try:
        return updateMovie(movieId, payload)
    except MovieNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{movieId}", status_code=status.HTTP_204_NO_CONTENT)
def removeMovie(movieId: int, admin: dict = Depends(requireAdmin)):
    try:
        deleteMovie(movieId)
    except MovieNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
