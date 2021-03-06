# Generated by Django 2.2.3 on 2020-05-10 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0012_auto_20200419_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='related_artists',
        ),
        migrations.CreateModel(
            name='SimilarTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.IntegerField()),
                ('other', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other', to='harmonize.Track')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track', to='harmonize.Track')),
            ],
        ),
    ]
