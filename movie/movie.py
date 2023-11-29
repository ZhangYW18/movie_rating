import csv
import os
import time

import numpy as np
import threading
import traceback

from django.db.models import Count, Avg, F
from django.http import JsonResponse, HttpRequest, Http404
from django.views.decorators.csrf import csrf_exempt

from rating_backend.settings import ARCHIVE_DATA_FOLDER, MAX_RATING, EPSILON_GLOBAL_DP, \
    SENSITIVITY_GLOBAL_DP, SCORE_MOVIE_RATING_DISTRIBUTION, SCORE_USER_RATING_DISTRIBUTION, DATASET_MAX_USER_ID, \
    DATASET_MAX_MOVIE_ID
from .models import Movie
from .models import Rating

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_csv_data(request, min_movie_id=0, max_movie_id=DATASET_MAX_MOVIE_ID, max_user_id=DATASET_MAX_USER_ID,
                  evaluate=False, evaluate_by_user=False):
    # Movie.objects.all().delete()
    Rating.objects.all().delete()
    if evaluate_by_user:
        Rating.objects.filter(user_id__lte=max_user_id).delete()
    else:
        # Movie.objects.filter(id__lte=max_movie_id).delete()
        Rating.objects.filter(movie_id__lte=max_movie_id).delete()
    with open(ARCHIVE_DATA_FOLDER + 'Netflix_Dataset_Movie.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count % 10000 == 0:
                print(f'Processed {line_count} lines for movie table.')
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if (not evaluate_by_user) and int(row[0]) > max_movie_id:
                    break
                m = Movie(id=row[0], year=row[1], name=row[2])
                m.save()
                line_count += 1
        print(f'Processed {line_count} lines for movie table.')

    rating_file_name = 'Netflix_Dataset_Rating_Sorted_By_User.csv' if evaluate_by_user else \
        'Netflix_Dataset_Rating_Sorted_By_Movie_User.csv'
    with open(ARCHIVE_DATA_FOLDER + rating_file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        pre_movie_id = -1
        movie_rate_user_count = 0
        for row in csv_reader:
            # if line_count > 10000:
            #     break
            if line_count % 1000 == 0:
                print(f'Processed {line_count} lines of ratings.')
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if evaluate_by_user:
                    if int(row[0]) > max_user_id:
                        break
                else:
                    if int(row[2]) < min_movie_id:
                        continue
                    if int(row[2]) > max_movie_id:
                        break
                    if int(row[0]) > max_user_id:
                        continue
                if evaluate:
                    if pre_movie_id != int(row[2]):
                        pre_movie_id = int(row[2])
                        movie_rate_user_count = 1
                    else:
                        # if movie_rate_user_count >= 1000:
                        #     continue
                        movie_rate_user_count = movie_rate_user_count + 1
                    request = HttpRequest()
                    request.POST['user_id'] = row[0]
                    request.POST['rating'] = row[1]
                    m = Rating(movie_id=Movie(id=int(row[2])), user_id=int(row[0]), rating=int(row[1]))
                    m.noise = add_noise(m, store_instantly=False)
                    m.save()
                else:
                    m = Rating(movie_id=Movie(id=int(row[2])), user_id=int(row[0]), rating=int(row[1]))
                    m.save()
                line_count += 1
        print(f'Processed {line_count} lines for rating table.')
    return JsonResponse({"msg": "load success"})


# Report noisy max
# Special case: when user modify the rating?
def add_noise(rating_obj, store_instantly=True):
    # Calculate the scores for each rating based on the average rating of a movie
    movie_ratings = Rating.objects.filter(movie_id=rating_obj.movie_id).values('rating')
    movie_rating_distribution = movie_ratings.annotate(count=Count('id'))
    # # # TODO debug
    # movie_noised_rating_distribution = movie_ratings.annotate(noised_rating=F('noise')+F('rating')) \
    #     .values('noised_rating').annotate(count=Count('id'))
    # print(movie_noised_rating_distribution)
    # print(movie_rating_distribution)
    movie_rating_nums = movie_ratings.count()
    scores = [0] * MAX_RATING
    for v in movie_rating_distribution.all():
        scores[v['rating'] - 1] = v['count'] * SCORE_MOVIE_RATING_DISTRIBUTION / movie_rating_nums

    # Add Laplace noise to the scores based on user's personal rating noise history
    user_rated_movies = Rating.objects.filter(user_id=rating_obj.user_id)
    # # TODO debug
    # user_rating_distribution = user_rated_movies\
    #     .values('noise')\
    #     .annotate(count=Count('id'))
    # print(user_rating_distribution)
    user_avg_noise = user_rated_movies.aggregate(Avg("noise", default=0))['noise__avg']

    # Normalize the laplace scores so that their sum is 1 and remains the same ratio
    # score_from_user_distribution = [laplace_sample(i + 1 - rating_obj.rating, -user_avg_noise) for i in range(0, MAX_RATING)]
    # sum_laplace_user = sum(score_from_user_distribution)
    # score_from_user_distribution = [score * SCORE_USER_RATING_DISTRIBUTION / sum_laplace_user for score in score_from_user_distribution]
    score_from_user_distribution = [abs(i + 1 - rating_obj.rating - (-user_avg_noise)) for i in range(0, MAX_RATING)]
    score_from_user_distribution = [np.exp(x) for x in score_from_user_distribution]
    min_tmp = min(score_from_user_distribution)
    score_from_user_distribution = [max(min_tmp * 10 - score, 0) for score in score_from_user_distribution]
    sum_laplace_user = sum(score_from_user_distribution)
    score_from_user_distribution = [score * SCORE_USER_RATING_DISTRIBUTION / sum_laplace_user for score in
                                    score_from_user_distribution]
    # print(user_avg_noise, rating_obj.rating, score_from_user_distribution)

    scores = [score_from_user_distribution[i] + score for i, score in enumerate(scores)]
    noisy_scores = [np.random.laplace(loc=0, scale=SENSITIVITY_GLOBAL_DP / EPSILON_GLOBAL_DP) + score
                    for score in scores]
    '''
    Optimization: exclude noise > 2.
    Turning it on will make the avg_rating closer to the avg_noised_rating,
    but make the variance less.
    '''
    # min_tmp = min(noisy_scores)
    # noisy_scores = [min_tmp-1 if abs(i+1-rating_obj.rating) > 2 else score for i, score in enumerate(noisy_scores)]

    ratings = range(1, MAX_RATING + 1)
    noised_rating = ratings[np.argmax(noisy_scores)]

    # Get selected noise and store it into DB
    noise = noised_rating - rating_obj.rating
    rating_obj.noise = noise
    if store_instantly:
        rating_obj.save()
    # print("noise added for rating", rating_obj.id)
    return noise


@csrf_exempt
def handle_rate(request, movie_id):
    try:
        rating = int(request.POST["rating"])
        if rating > MAX_RATING or rating <= 0:
            return JsonResponse({"msg": "rating is not in the right range"}, status=400)
        movie_id = int(movie_id)
        user_id = int(request.POST["user_id"])

        old_r = Rating.objects.filter(movie_id=movie_id, user_id=user_id)
        r = Rating(movie_id=Movie(id=movie_id), user_id=user_id, rating=rating)
        if old_r.count() == 1:
            r = old_r.first()
            r.rating = rating
        elif old_r.count() > 1:
            return JsonResponse({"msg": "a user has more than one rating for a movie"}, status=500)
        r.save()

        # open a new thread to handle differential privacy
        th = threading.Thread(target=add_noise, args=(r,))
        th.start()

        return JsonResponse({"msg": "rate success"})
    except Exception as e:
        print(''.join(traceback.TracebackException.from_exception(e).format()))
        return JsonResponse({"msg": "internal error"}, status=500)


def get_variance_for_distribution(rating_distribution):
    ratings = list(range(1, MAX_RATING + 1))
    counts = [0] * MAX_RATING
    for v in rating_distribution.all():
        if 'rating' in v:
            counts[v['rating'] - 1] = v['count']
        else:
            counts[v['noised_rating'] - 1] = v['count']
    ratings = np.array(ratings)
    counts = np.array(counts)
    weighted_mean = np.average(ratings, weights=counts)
    weighted_variance = np.average((ratings - weighted_mean) ** 2, weights=counts)
    return counts, np.round(weighted_variance, decimals=2)


def export_movie_rating_distribution(max_movie_id=DATASET_MAX_MOVIE_ID, time_now=str(int(time.time()))):
    with open(ARCHIVE_DATA_FOLDER + 'Evaluate_Result_Movie' + time_now + '.csv', 'w') as f:
        writer = csv.writer(f)
        header = ['movie_id', 'avg_rating', 'avg_noised_rating',
                  'rating_count', 'rating_variance',
                  'noised_count', 'noised_variance']
        writer.writerow(header)
        for i in range(0, max_movie_id + 1):
            if i % 100 == 0:
                print(f"Processed movies with max_movie_id<{i}.")
            movie_ratings = Rating.objects.filter(movie_id=i)
            if movie_ratings.count() == 0:
                continue
            movie_avg_noise = movie_ratings.aggregate(Avg("noise", default=0))['noise__avg']
            movie_avg_rating = movie_ratings.aggregate(Avg("rating", default=0))['rating__avg']
            movie_rating_distribution = movie_ratings.values('rating').annotate(count=Count('id')).order_by('rating')
            movie_noised_rating_distribution = movie_ratings.annotate(noised_rating=F('noise') + F('rating')) \
                .values('noised_rating').annotate(count=Count('id')).order_by('noised_rating')
            counts, variance = get_variance_for_distribution(movie_rating_distribution)
            n_counts, n_variance = get_variance_for_distribution(movie_noised_rating_distribution)
            data = [i, "{:.1f}".format(movie_avg_rating), "{:.1f}".format(movie_avg_rating + movie_avg_noise),
                    counts, variance,
                    n_counts, n_variance]
            writer.writerow(data)
        print(f"Processed movies with max_movie_id<{max_movie_id}")


def export_user_rating_distribution(max_user_id=DATASET_MAX_USER_ID, time_now=str(int(time.time()))):
    with open(ARCHIVE_DATA_FOLDER + 'Evaluate_Result_User' + time_now + '.csv', 'w') as f:
        writer = csv.writer(f)
        header = ['user_id', 'avg_rating', 'avg_noised_rating',
                  'rating_count', 'rating_variance',
                  'noised_count', 'noised_variance']
        writer.writerow(header)
        for i in range(0, max_user_id + 1):
            if i % 10000 == 0:
                print(f"Processed users with max_user_id<{i}.")
            user_ratings = Rating.objects.filter(user_id=i)
            if user_ratings.count() == 0:
                continue
            user_avg_noise = user_ratings.aggregate(Avg("noise", default=0))['noise__avg']
            user_avg_rating = user_ratings.aggregate(Avg("rating", default=0))['rating__avg']
            user_rating_distribution = user_ratings.values('rating').annotate(count=Count('id')).order_by('rating')
            user_noised_rating_distribution = user_ratings.annotate(noised_rating=F('noise') + F('rating')) \
                .values('noised_rating').annotate(count=Count('id')).order_by('noised_rating')
            counts, variance = get_variance_for_distribution(user_rating_distribution)
            n_counts, n_variance = get_variance_for_distribution(user_noised_rating_distribution)
            data = [i, "{:.1f}".format(user_avg_rating), "{:.1f}".format(user_avg_rating + user_avg_noise),
                    counts, variance,
                    n_counts, n_variance]
            writer.writerow(data)
        print(f"Processed users with max_user_id<{max_user_id}")


def handle_evaluate_by_movie(request, max_movie_id=DATASET_MAX_MOVIE_ID):
    # load_csv_data(request, max_movie_id=max_movie_id, evaluate=True)
    print(f"Waiting for result exportation...")
    time_now = str(int(time.time()))
    export_movie_rating_distribution(max_movie_id=max_movie_id, time_now=time_now)
    export_user_rating_distribution(time_now=time_now)
    return JsonResponse({"msg": "evaluate success"})


def handle_evaluate_by_user(request, max_user_id=DATASET_MAX_USER_ID):
    load_csv_data(request, max_user_id=max_user_id, evaluate=True, evaluate_by_user=True)
    print(f"Waiting for result exportation...")
    time_now = str(int(time.time()))
    export_movie_rating_distribution(time_now=time_now)
    export_user_rating_distribution(max_user_id=max_user_id, time_now=time_now)
    return JsonResponse({"msg": "evaluate success"})


def get_movie(request, id):
    try:
        movie = Movie.objects.get(pk=id)
        return JsonResponse({
            'id': movie.id,
            'year': movie.year,
            'name': movie.name
        })
    except Movie.DoesNotExist:
        raise Http404("Movie does not exist")


def get_movie_rating_dist(request):
    # Assume movie ID is provided as a query parameter
    movie_id = request.GET.get('movie_id')
    if not movie_id:
        return JsonResponse({'error': 'Movie ID is required.'}, status=400)

    distribution = Rating.objects.filter(movie_id=int(movie_id)).values('rating').annotate(
        count=Count('rating')).order_by('rating')
    print(distribution)
    distribution_data = {rating['rating']: rating['count'] for rating in distribution}

    return JsonResponse(distribution_data)


def get_noise_value_bar_diagram(request):
    y = [[0 for _ in range(5)] for _ in range(6)]

    ratings = Rating.objects.filter(movie_id__lt=306)
    for rating in ratings:
        # print(rating.rating)
        y[0][abs(rating.noise)] = y[0][abs(rating.noise)] + 1
        y[rating.rating][rating.rating + rating.noise - 1] = y[rating.rating][rating.rating + rating.noise - 1] + 1

    for i in range(0, 6):
        plt.xlabel('Delta (Noise)')
        plt.ylabel('Counts')
        if i == 0:
            x = range(0, 5)
            plt.title('Noise Value Stats')
            plt.bar(x, y[i])
        else:
            x = range(1, 6)
            plt.title('Noised Ratings for Rating ' + str(i))
            plt.bar(x, y[i])
        plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1)
        plt.savefig(os.path.join(os.path.dirname(__file__), f'diagrams/noise_value_count_{i}.png'))
        plt.clf()

    return JsonResponse({"msg": "plot success"})


def get_avg_noise_for_movies(request, movie_id):
    x = [2 ** i for i in range(1, 25)]
    y = [0] * 25

    ratings = Rating.objects.filter(movie_id=movie_id).order_by("user_id")
    sum_noise = 0
    ix = 0
    for i, rating in enumerate(ratings):
        sum_noise += rating.noise
        if i + 1 == x[ix]:
            y[ix] = sum_noise / float(i + 1)
            ix = ix + 1
    x[ix] = ratings.count()
    y[ix] = sum_noise / float(x[ix])
    ix = ix + 1
    x, y = x[0:ix], y[0:ix]
    # print(x)
    # print(y)

    plt.xlabel('Number of Ratings')
    plt.ylabel('Average Noise')
    plt.title('Average Noise Trend for Movie #' + str(movie_id))
    plt.xscale("log")
    plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1)
    plt.plot(x, y, marker='o', color='b')
    plt.savefig(os.path.join(os.path.dirname(__file__), f'diagrams/avg_noise_movie_{movie_id}.png'))
    plt.clf()

    return JsonResponse({"msg": "plot success"})
