# Generated by Django 5.0.4 on 2024-04-21 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default=1, max_length=150, verbose_name='Имя'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(default=123, max_length=150, verbose_name='Фамилия'),
            preserve_default=False,
        ),
    ]
