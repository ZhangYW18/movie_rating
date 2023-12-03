import React, { useEffect, useState } from "react"
import "./movie.css"
import { useParams } from "react-router-dom"

const Movie = () => {
    const [currentMovieDetail, setMovie] = useState()
    const [ratingDistribution, setRatingDistribution] = useState({});
    const [noisedRatingDistribution, setNoisedRatingDistribution] = useState({});
    const { id } = useParams()

    useEffect(() => {
        getData();
        getRatingDistribution();
        window.scrollTo(0, 0);
    }, [id])

    const getData = () => {
        fetch(`https://api.themoviedb.org/3/movie/${id}?api_key=4e44d9029b1270a757cddc766a1bcb63&language=en-US`)
            .then(res => res.json())
            .then(data => setMovie(data))
    }

    const getRatingDistribution = () => {
        fetch(`http://127.0.0.1:8000/v1/movie/get_rating_distribution/${id % 50}`)
            .then(res => res.json())
            .then(data => {
                setRatingDistribution(data.rating_distribution)
                setNoisedRatingDistribution(data.noised_rating_distribution)
            })
    }

    // render bars in two lines
    const renderRatingDistribution = () => {
        const maxCount = Math.max(
            ...Object.values(ratingDistribution),
            ...Object.values(noisedRatingDistribution)
        );

        return Object.entries(ratingDistribution).map(([rating, count]) => {
            const noisedCount = noisedRatingDistribution[rating] || 0;
            return (
                <>
                    <div key={`raw-${rating}`} className="movie__ratingDistributionRow">
                        <span className="movie__ratingNumber">{rating}</span>
                        <div className="movie__ratingBar movie__ratingBar--raw" style={{ width: `${(count / maxCount) * 100}%` }} title={`Rating ${rating}: ${count}`}>
                            {count}
                        </div>
                    </div>
                    <div key={`noised-${rating}`} className="movie__ratingDistributionRow movie__ratingDistributionRow--noised">
                        <span className="movie__ratingNumber">{rating}</span>
                        <div className="movie__ratingBar movie__ratingBar--noised" style={{ width: `${(noisedCount / maxCount) * 100}%` }} title={`Noised Rating ${rating}: ${noisedCount}`}>
                            {noisedCount}
                        </div>
                    </div>
                </>
            );
        });
    };

    // render bars in the same line
    // const renderRatingDistribution = () => {
    //     // Assuming the maximum count for scaling the bar sizes is needed from both distributions
    //     const maxCount = Math.max(
    //         ...Object.values(ratingDistribution),
    //         ...Object.values(noisedRatingDistribution)
    //     );

    //     return Object.entries(ratingDistribution).map(([rating, count]) => {
    //         const noisedCount = noisedRatingDistribution[rating] || 0;
    //         return (
    //             <div key={rating} className="movie__ratingDistributionRow">
    //                 <span className="movie__ratingNumber">{rating}</span>
    //                 <div className="movie__ratingBarsContainer">
    //                     <div className="movie__ratingBar" style={{ width: `${(count / maxCount) * 100}%` }} title={`Rating ${rating}: ${count}`}></div>
    //                     <div className="movie__ratingBar movie__ratingBar--noised" style={{ width: `${(noisedCount / maxCount) * 100}%` }} title={`Noised Rating ${rating}: ${noisedCount}`}></div>
    //                 </div>
    //                 <span className="movie__ratingCount">{count}</span>
    //                 <span className="movie__noisedRatingCount">{noisedCount}</span>
    //             </div>
    //         );
    //     });
    // };

    const calculateAverageNoisedRating = () => {
        const totalNoisedRatings = Object.entries(noisedRatingDistribution)
            .reduce((acc, [rating, count]) => acc + (parseInt(rating) * count), 0);
        const totalCount = Object.values(noisedRatingDistribution).reduce((acc, count) => acc + count, 0);
        return totalCount > 0 ? (totalNoisedRatings / totalCount).toFixed(2) : 0;
    };

    const averageNoisedRating = calculateAverageNoisedRating();

    return (
        <div className="movie">
            <div className="movie__intro">
                <img className="movie__backdrop" src={`https://image.tmdb.org/t/p/original${currentMovieDetail ? currentMovieDetail.backdrop_path : ""}`} />
            </div>
            <div className="movie__detail">
                <div className="movie__detailLeft">
                    <div className="movie__posterBox">
                        <img className="movie__poster" src={`https://image.tmdb.org/t/p/original${currentMovieDetail ? currentMovieDetail.poster_path : ""}`} />
                    </div>
                </div>
                <div className="movie__detailRight">
                    <div className="movie__detailRightTop">
                        <div className="movie__name">{currentMovieDetail ? currentMovieDetail.original_title : ""}</div>
                        <div className="movie__tagline">{currentMovieDetail ? currentMovieDetail.tagline : ""}</div>
                        <div className="movie__rating">
                            {averageNoisedRating} <i className="fas fa-star" />
                            <span className="movie__voteCount">{`(${Object.values(noisedRatingDistribution).reduce((acc, count) => acc + count, 0)} votes)`}</span>
                        </div>
                        <div className="movie__runtime">{currentMovieDetail ? currentMovieDetail.runtime + " mins" : ""}</div>
                        <div className="movie__releaseDate">{currentMovieDetail ? "Release date: " + currentMovieDetail.release_date : ""}</div>
                        <div className="movie__genres">
                            {
                                currentMovieDetail && currentMovieDetail.genres
                                    ?
                                    currentMovieDetail.genres.map(genre => (
                                        <><span className="movie__genre" id={genre.id}>{genre.name}</span></>
                                    ))
                                    :
                                    ""
                            }
                        </div>
                    </div>
                    <div className="movie__detailRightBottom">
                        <div className="synopsisText">Synopsis</div>
                        <div>{currentMovieDetail ? currentMovieDetail.overview : ""}</div>
                    </div>

                    <div className="movie__heading">Rating Distribution</div>
                    <div className="movie__ratingDistribution">
                        {renderRatingDistribution()}
                    </div>

                </div>
            </div>
            <div className="movie__links">
                <div className="movie__heading">Useful Links</div>
                {
                    currentMovieDetail && currentMovieDetail.homepage && <a href={currentMovieDetail.homepage} target="_blank" style={{ textDecoration: "none" }}><p><span className="movie__homeButton movie__Button">Homepage <i className="newTab fas fa-external-link-alt"></i></span></p></a>
                }
                {
                    currentMovieDetail && currentMovieDetail.imdb_id && <a href={"https://www.imdb.com/title/" + currentMovieDetail.imdb_id} target="_blank" style={{ textDecoration: "none" }}><p><span className="movie__imdbButton movie__Button">IMDb<i className="newTab fas fa-external-link-alt"></i></span></p></a>
                }
            </div>
            <div className="movie__heading">Production companies</div>
            <div className="movie__production">
                {
                    currentMovieDetail && currentMovieDetail.production_companies && currentMovieDetail.production_companies.map(company => (
                        <>
                            {
                                company.logo_path
                                &&
                                <span className="productionCompanyImage">
                                    <img className="movie__productionComapany" src={"https://image.tmdb.org/t/p/original" + company.logo_path} />
                                    <span>{company.name}</span>
                                </span>
                            }
                        </>
                    ))
                }
            </div>
        </div>
    )
}

export default Movie