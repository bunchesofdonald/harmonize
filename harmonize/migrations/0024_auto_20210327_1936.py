# Generated by Django 3.0.6 on 2021-03-27 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0023_auto_20210317_2242'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track', to='harmonize.Track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harmonize.SpotifyUser')),
            ],
        ),
        migrations.AlterField(
            model_name='smartplaylist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harmonize.SpotifyUser'),
        ),
        migrations.DeleteModel(
            name='SimilarTrack',
        ),
    ]