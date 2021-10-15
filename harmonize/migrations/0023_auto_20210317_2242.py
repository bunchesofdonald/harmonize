# Generated by Django 3.0.6 on 2021-03-17 22:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('harmonize', '0022_smartplaylist_profile'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='SpotifyUser',
        ),
        migrations.RenameField(
            model_name='smartplaylist',
            old_name='profile',
            new_name='user',
        ),
    ]