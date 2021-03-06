# Generated by Django 3.2.6 on 2021-11-30 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.URLField(blank=True, default=None)),
                ('name', models.CharField(max_length=32)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('old_price', models.FloatField(blank=True, default=0)),
                ('amount_remaining', models.PositiveSmallIntegerField()),
                ('description', models.TextField(max_length=1000)),
                ('datetime_created', models.DateTimeField(auto_now=True)),
                ('size', models.CharField(max_length=16)),
                ('color', models.CharField(max_length=32)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=32)),
                ('review_text', models.TextField(max_length=1000)),
                ('liked', models.BooleanField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]
