# Generated by Django 4.2.7 on 2023-11-18 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_alter_movie_table_alter_rating_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rating',
            name='noise',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelTable(
            name='movie',
            table=None,
        ),
        migrations.AlterModelTable(
            name='rating',
            table=None,
        ),
    ]
