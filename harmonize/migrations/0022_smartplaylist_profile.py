# Generated by Django 3.0.6 on 2021-03-15 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0021_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartplaylist',
            name='profile',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='harmonize.Profile'),
            preserve_default=False,
        ),
    ]
