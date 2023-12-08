# Generated by Django 4.2.7 on 2023-12-07 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0002_alter_book_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorphoto',
            name='author_photo',
            field=models.ImageField(blank=True, null=True, upload_to='image'),
        ),
        migrations.AlterField(
            model_name='book',
            name='publishing',
            field=models.DateField(blank=True, null=True),
        ),
    ]
