# Generated by Django 5.1.7 on 2025-05-05 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinephoria_webapp', '0015_remove_seance_jour_semaine_film_duree_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='affiche',
            field=models.ImageField(blank=True, null=True, upload_to='films/'),
        ),
    ]
