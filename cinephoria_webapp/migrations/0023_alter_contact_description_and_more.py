# Generated by Django 5.1.7 on 2025-05-22 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinephoria_webapp', '0022_remove_utilisateur_doit_changer_mdp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='contact',
            name='objet_demande',
            field=models.CharField(max_length=100),
        ),
    ]
