# Generated by Django 3.2.6 on 2021-10-06 20:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='like',
            new_name='liked',
        ),
    ]
