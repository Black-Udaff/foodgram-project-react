# Generated by Django 5.0.4 on 2024-04-16 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ricept', '0002_alter_ingredient_options_alter_tag_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient_recipe',
            old_name='ingredient_id',
            new_name='ingredient',
        ),
        migrations.RenameField(
            model_name='ingredient_recipe',
            old_name='recipe_id',
            new_name='recipe',
        ),
    ]