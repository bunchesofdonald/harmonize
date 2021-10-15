# Generated by Django 2.2.3 on 2019-07-23 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harmonize', '0003_smartplaylist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='tag',
            name='useful',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='smartplaylist',
            name='exclude',
            field=models.ManyToManyField(blank=True, related_name='_smartplaylist_exclude_+', to='harmonize.Tag'),
        ),
        migrations.AlterField(
            model_name='weightedtag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weighted', to='harmonize.Tag'),
        ),
    ]
