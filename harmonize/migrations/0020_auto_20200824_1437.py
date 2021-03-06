# Generated by Django 3.0.6 on 2020-08-24 14:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0019_playlisthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlisthistory',
            name='added_date',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2020, 8, 24, 14, 37, 10, 671826, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterIndexTogether(
            name='playlisthistory',
            index_together={('playlist', 'track', 'added_date')},
        ),
        migrations.RemoveField(
            model_name='playlisthistory',
            name='count',
        ),
        migrations.RemoveField(
            model_name='playlisthistory',
            name='last_date',
        ),
    ]
