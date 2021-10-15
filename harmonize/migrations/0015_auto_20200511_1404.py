# Generated by Django 2.2.3 on 2020-05-11 14:04

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0014_auto_20200510_1738'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smartplaylist',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='smartplaylist',
            name='excluded_albums',
        ),
        migrations.RemoveField(
            model_name='smartplaylist',
            name='excluded_artists',
        ),
        migrations.RemoveField(
            model_name='smartplaylist',
            name='included_albums',
        ),
        migrations.RemoveField(
            model_name='smartplaylist',
            name='n',
        ),
        migrations.AddField(
            model_name='smartplaylist',
            name='filter',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=''),
            preserve_default=False,
        ),
    ]
