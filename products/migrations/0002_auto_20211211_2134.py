# Generated by Django 3.2.6 on 2021-12-11 21:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='author_name',
        ),
        migrations.AddField(
            model_name='review',
            name='author',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='commentaries', to=settings.AUTH_USER_MODEL),
        ),
    ]
