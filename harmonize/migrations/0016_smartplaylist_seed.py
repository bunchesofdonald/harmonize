# Generated by Django 2.2.3 on 2020-05-11 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0015_auto_20200511_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartplaylist',
            name='seed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='harmonize.Track'),
        ),
    ]
