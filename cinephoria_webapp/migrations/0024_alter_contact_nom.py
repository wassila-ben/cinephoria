# Generated by Django 5.1.7 on 2025-05-22 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinephoria_webapp', '0023_alter_contact_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='nom',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
