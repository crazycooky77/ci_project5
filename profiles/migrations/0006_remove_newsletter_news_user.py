# Generated by Django 4.2.1 on 2024-06-29 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_newsletter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsletter',
            name='news_user',
        ),
    ]
