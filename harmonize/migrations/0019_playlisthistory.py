# Generated by Django 3.0.6 on 2020-08-23 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0018_smartplaylist_track_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaylistHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_date', models.DateField(auto_now=True)),
                ('count', models.IntegerField(default=0)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harmonize.SmartPlaylist')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harmonize.Track')),
            ],
        ),
    ]