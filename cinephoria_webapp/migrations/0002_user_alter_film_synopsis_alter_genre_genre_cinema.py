# Generated by Django 5.1.4 on 2024-12-19 15:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinephoria_webapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Identifiant', models.CharField(unique=True, verbose_name=20)),
                ('Nom', models.CharField(verbose_name=20)),
                ('Prenom', models.CharField(verbose_name=20)),
                ('email', models.CharField(unique=True, verbose_name=40)),
            ],
        ),
        migrations.AlterField(
            model_name='film',
            name='Synopsis',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='genre',
            name='Genre',
            field=models.CharField(),
        ),
        migrations.CreateModel(
            name='cinema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nom', models.CharField(verbose_name=50)),
                ('Adresse', models.CharField(verbose_name=200)),
                ('CP', models.CharField(verbose_name=8)),
                ('Ville', models.CharField(verbose_name=50)),
                ('Pays', models.CharField(verbose_name=10)),
                ('Telephone', models.CharField(verbose_name=20)),
                ('ID_seance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cinephoria_webapp.seance')),
            ],
        ),
    ]
