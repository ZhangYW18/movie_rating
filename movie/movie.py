from django.http import JsonResponse, Http404

from rating_backend.settings import ARCHIVE_DATA_FOLDER
from django.db.models import Count
from .models import Movie, Rating
import csv


def load_csv_data(request):
    with open(ARCHIVE_DATA_FOLDER + 'Netflix_Dataset_Movie.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count % 10000 == 0:
                print(f'Processed {line_count} lines of movies.')
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                m = Movie(id=row[0], year=row[1], name=row[2])
                m.save()
                line_count += 1
        print(f'Processed {line_count} lines for movie table.')
    with open(ARCHIVE_DATA_FOLDER + 'Netflix_Dataset_Rating.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count % 10000 == 0:
                print(f'Processed {line_count} lines of ratings.')
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if int(row[2]) > 500:
                    break
                m = Rating(movie_id=Movie(id=int(row[2])), user_id=row[0], rating=row[1])
                m.save()
                line_count += 1
        print(f'Processed {line_count} lines for rating table.')
    return JsonResponse({"msg": "load success"})

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
    
    distribution = Rating.objects.filter(movie_id=int(movie_id)).values('rating').annotate(count=Count('rating')).order_by('rating')
    print(distribution)
    distribution_data = {rating['rating']: rating['count'] for rating in distribution}
    
    return JsonResponse(distribution_data)