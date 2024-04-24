# Generated by Django 4.2.1 on 2024-04-24 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0004_saveditems_purchases'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
