# Generated by Django 5.1.5 on 2025-01-20 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(default='profile_pictures/default.jpg', upload_to='profile_pictures'),
        ),
    ]
