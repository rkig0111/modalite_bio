# Generated by Django 4.0 on 2023-08-16 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagerie', '0003_liste_serveur_connect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liste',
            name='aet',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='liste',
            name='hostname',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='liste',
            name='modalite',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='liste',
            name='systeme',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]