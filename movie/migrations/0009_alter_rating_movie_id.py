# Generated by Django 4.2.7 on 2023-11-19 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0008_rating_unique_user_movie_combination'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='movie_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.movie'),
        ),
    ]
