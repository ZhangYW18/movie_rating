
# Installation

## Activate venv
(TODO)

## Install Dependencies

To install packages
```shell
pip install -r requirements.txt 
```

To export packages
```shell
pipreqs . --force
```

# Database Config

Reference: https://docs.djangoproject.com/en/4.2/ref/databases/#mysql-notes

Install MySQL firstly.

Install mysqlclient on MacOS: see https://github.com/PyMySQL/mysqlclient
```shell
$ # Assume you are activating Python 3 venv
$ brew install mysql-client pkg-config
$ export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
$ pip install mysqlclient
```

Modify the database setting in `rating_backend/settings.py`.

# Load Data

Download the data from
https://www.kaggle.com/datasets/rishitjavia/netflix-movie-rating-dataset/data, and put them under `./archive`.

Run the project using `python manage.py runserver` and call `http://127.0.0.1:8000/v1/movie/load`.

# API List v1

- Load Data     GET /v1/movie/load
  
  Load data from csv files.

- RateMovie 	POST /v1/movie/:id/rate/   userId
  
  Store a user's rating for a movie, and add noise for it.

- GetMovie (including ratings).  GET  /v1/movie/:id
  
  Get all the info about a movie.

- GetMovieRatingDistribution  GET. /v1/movie/rating_distribution
  
  Get distribution of ratings for a specific movie.

- GetUserRatings. GET /v1/user/rating
  
  Get all ratings of a user.

# Documents

[The Exponential Mechanism](https://programming-dp.com/ch9.html)

