from django.http import JsonResponse

from rating_backend.settings import ARCHIVE_DATA_FOLDER
from .models import Movie, Rating
import csv


def load_csv_data(request):
    with open(ARCHIVE_DATA_FOLDER + 'Netflix_Dataset_Movie.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count % 10000 == 0:
                print(f'Processed {line_count} lines.')
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
                print(f'Processed {line_count} lines.')
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if int(row[2]) > 500:
                    break
                m = Rating(movie_id=row[2], user_id=row[0], rating=row[1])
                m.save()
                line_count += 1
        print(f'Processed {line_count} lines for rating table.')
    return JsonResponse({"msg": "load success"})
