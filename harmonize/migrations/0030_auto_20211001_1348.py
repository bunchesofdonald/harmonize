# Generated by Django 3.2 on 2021-10-01 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0029_auto_20210723_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(to='harmonize.Genre'),
        ),
    ]
