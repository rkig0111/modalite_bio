# Generated by Django 4.0 on 2023-10-24 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagerie', '0006_rename_serveurid_modalite_serveur_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machine',
            old_name='vlanid',
            new_name='vlan',
        ),
        migrations.RenameField(
            model_name='projet',
            old_name='logicielid',
            new_name='logiciel',
        ),
    ]
