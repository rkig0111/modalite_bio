# Generated by Django 4.0 on 2023-10-26 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagerie', '0009_alter_machine_options_alter_modalite_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serveur',
            name='modalite',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='srvdicom',
        ),
    ]
