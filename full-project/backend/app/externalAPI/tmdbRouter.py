from fastapi import APIRouter, HTTPException
from app.externalAPI.tmdbService import (
    getMovieDetailsByName,
    getMovieDetailsById,
    getRecommendationsByName,
    getRecommendationsById,
)
from app.schemas.movie import Movie
from app.services.movieService import getMovieById
from .tmdbSchema import TMDbMovie, TMDbRecommendation

router = APIRouter(prefix="/tmdb", tags=["tmdb"])


@router.get("/details/name/{movieName}", response_model=TMDbMovie)
def movieDetailsByName(movieName: str):
    details = getMovieDetailsByName(movieName)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found")
    return details

@router.get("/details/{movieId}", response_model=TMDbMovie)
def movieDetailsById(movieId: int):
    movie = getMovieById(movieId) 
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    tmdbId = movie.tmdbId
    details = getMovieDetailsById(tmdbId)
    if details is None:
        raise HTTPException(status_code=404, detail="TMDB movie not found")
    return details


@router.get("/recommendations/name/{movieName}", response_model=list[TMDbRecommendation])
def recommendationsByName(movieName: str):
    return getRecommendationsByName(movieName)



@router.get("/recommendations/{movieId}", response_model=list[TMDbRecommendation])
def recommendationsById(movieId: int):
    
    movie = getMovieById(movieId)  
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    #Extract tmdbId from our DB entry
    tmdbId = movie.tmdbId

    #Fetch recommendations by TMDb ID
    return getRecommendationsById(tmdbId)
