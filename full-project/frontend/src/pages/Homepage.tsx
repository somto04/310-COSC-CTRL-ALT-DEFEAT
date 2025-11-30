import { useEffect, useState } from "react";

export default function Homepage() {
    type Movie = {
        id: number;
        tmdbId?: number;
        title: string;
        poster?: string | null;
        overview?: string;
        rating?: number;
    };
    
    const [movies, setMovies] = useState<Movie[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(false);
    const [filterGenre, setFilterGenre] = useState("");
    const [filterYear, setFilterYear] = useState("");
    const [filterDirector, setFilterDirector] = useState("");
    const [filterStar, setFilterStar] = useState("");


    const fetchMoviesWithPosters = async (moviesList: any[]) => {
        const moviesWithPosters = await Promise.all(
            moviesList.map(async (movie: any) => {
                const tmdbRes = await fetch(
                    `http://localhost:8000/tmdb/details/${movie.id}`
                );

                const tmdbData = await tmdbRes.json();
                return {
                    id: movie.id,
                    title: movie.title,
                    poster: tmdbData.poster || null,
        };
      })
    );
    return moviesWithPosters;
  };
  
  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/movies/")
    .then((res) => res.json())
    .then(async (moviesList) => {
        const moviesWithPosters = await fetchMoviesWithPosters(moviesList);
        setMovies(moviesWithPosters);
        setLoading(false);
    })
    .catch((err) => {
        console.error(err);
        setLoading(false);
    });
    }, []);
    
    useEffect(() => {
        const fetchFilteresMovies = async () => {
            try {
                let url = "http://localhost:8000/movies/filter?";
                const params = new URLSearchParams();

                if (searchTerm) params.append("query", searchTerm);
                if (filterGenre) params.append("genre", filterGenre);
                if (filterYear) {
                    const decadeMap: { [key: string]: number } = {
                        "60s": 1960,
                        "70s": 1970,
                        "80s": 1980,
                        "90s": 1990,
                        "2000s": 2000,
                        "10s": 2010,
                        "20s": 2020,
                    };
                    const yearValue = decadeMap[filterYear];
                    if (yearValue) params.append("year", String(yearValue));
                }
                if (filterDirector) params.append("director", filterDirector);
                if (filterStar) params.append("star", filterStar);

                const res = await fetch(url + params.toString());

                if (res.status === 404) {
                    setMovies([]);
                    return;
                }
                
                const data = await res.json();
                if (!Array.isArray(data)) {
                    setMovies([]);
                    return;
                }
                const moviesWithPosters = await fetchMoviesWithPosters(data);
                setMovies(moviesWithPosters);
            }
            catch (err) {
                console.error("Error fetching movies: ", err);
            }
    };
    fetchFilteresMovies();
}, [searchTerm, filterDirector, filterStar, filterGenre, filterYear]);

 return (
    <div style={{ padding: "2rem", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Movies</h1>

      {/* SEARCH BOX */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", height: "50px" }}>
      <input
        type="text"
        placeholder="Search movies..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{
          padding: "0.5rem",
          width: "100%",
          marginBottom: "1rem",
          fontSize: "1rem",
        }}
      />

      <select
      value={filterGenre}
      onChange={(e) => setFilterGenre(e.target.value)}
      style={{ padding: "0.5rem", fontSize: "1rem", height: "50px" }}
      >
      
      <option value="">All Genres</option>
      <option value="action">Action</option>
      <option value="comedy">Comedy</option>
      <option value="drama">Drama</option>
      <option value="adventure">Adventure</option>
      <option value="scifi">Sci-Fi</option>
      <option value="crime">Crime</option>
      <option value="romance">Romance</option>
      <option value="thriller">Thriller</option>
      <option value="horror">Horror</option>
      </select>

      <select
      value={filterYear}
      onChange={(e) => setFilterYear(e.target.value)}
      style={{ padding: "0.5rem", fontSize: "1rem", height: "50px" }}
      >
      
      <option value="">All years</option>
      <option value="60s">60s</option>
      <option value="70s">70s</option>
      <option value="80s">80s</option>
      <option value="90s">90s</option>
      <option value="2000s">2000s</option>
      <option value="2010s">2010s</option>
      <option value="2020s">2020s</option>
      </select>

      <select
      value={filterDirector}
      onChange={(e) => setFilterDirector(e.target.value)}
      style={{ padding: "0.5rem", fontSize: "1rem", height: "50px" }}
      >
      
      <option value="">All directors</option>
      <option value="Anthony Russo">Anthony Russo</option>
      <option value="Joe Russo">Joe Russo</option>
      <option value="Robert Zemeckis">Robert Zemeckis</option>
      <option value="Chad Stahelski">Chad Stahelski</option>
      <option value="Todd Phillips">Todd Phillips</option>
      <option value="Daniel Espinosa">Daniel Espinosa</option>
      <option value="Quentin Tarantino">Quentin Tarantino</option>
      </select>      
      
      <select
      value={filterStar}
      onChange={(e) => setFilterStar(e.target.value)}
      style={{ padding: "0.5rem", fontSize: "1rem", height: "50px" }}
      >
      
      <option value="">All stars</option>
      <option value="John Travolta">John Travolta</option>
      <option value="Samuel L. Jackson">Samuel L. Jackson</option>
      <option value="Zendaya">Zendaya</option>
      <option value="Benedict Cumberbatch">Benedict Cumberbatch</option>
      <option value="Tom Holland">Tom Holland</option>
      <option value="Robert Downey Jr.">Robert Downey Jr.</option>
      <option value="Keanu Reeves">Keanu Reeves</option>
      </select>
      </div>


      {/* MOVIES */}
      <section style={{ marginTop: "2rem" }}>

        {movies.length === 0 ? (
          <p>No movies yet.</p>
        ) : (
          <ul style={{ paddingLeft: "1rem" }}>
            {movies.map((movie) => (
              <li
                key={movie.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginBottom: "1rem",
                  cursor: "pointer",
                }}
                onClick={() => {}}
              >
                {movie.poster && (
                  <img
                    src={movie.poster}
                    alt={movie.title}
                    style={{
                      width: "60px",
                      height: "90px",
                      objectFit: "cover",
                      border: "1px solid black",
                    }}
                  />
                )}

                <span>{movie.title}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}