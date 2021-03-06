# Generated by Django 2.2.3 on 2019-07-22 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0002_auto_20190722_0456'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartPlaylist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('spotify_uri', models.CharField(blank=True, max_length=255, unique=True)),
                ('threshold', models.PositiveSmallIntegerField()),
                ('exclude', models.ManyToManyField(related_name='_smartplaylist_exclude_+', to='harmonize.Tag')),
                ('include', models.ManyToManyField(related_name='_smartplaylist_include_+', to='harmonize.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
