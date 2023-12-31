# Generated by Django 4.2.7 on 2023-11-19 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0007_alter_movie_id'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('user_id', 'movie_id'), name='unique_user_movie_combination'),
        ),
    ]
