# Generated by Django 4.0 on 2023-10-23 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imagerie', '0005_rename_mod_appareilid_modalite_appareilid_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modalite',
            old_name='serveurid',
            new_name='serveur',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='bddid',
            new_name='bdd',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='comptesid',
            new_name='comptes',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='projetid',
            new_name='projet',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='rasid',
            new_name='ras',
        ),
        migrations.RenameField(
            model_name='serveur',
            old_name='resspartageid',
            new_name='resspartage',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='addrip',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='appareilid',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='appareiltypeid',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='datecreat',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='datemodif',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='datereforme',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='etablissementid',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='hostname',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='inventaire',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='localisationid',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='marqueid',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='systeme',
        ),
        migrations.RemoveField(
            model_name='modalite',
            name='vlanid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='addrip',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='appareilid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='appareiltypeid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='datecreat',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='datemodif',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='datereforme',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='etablissementid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='hostname',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='inventaire',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='localisationid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='marqueid',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='systeme',
        ),
        migrations.RemoveField(
            model_name='serveur',
            name='vlanid',
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addrip', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('hostname', models.CharField(blank=True, max_length=30, null=True)),
                ('systeme', models.CharField(blank=True, max_length=30, null=True)),
                ('inventaire', models.CharField(blank=True, max_length=24, null=True)),
                ('datecreat', models.DateTimeField(auto_now_add=True, verbose_name='date de création')),
                ('datemodif', models.DateTimeField(auto_now=True, verbose_name='date de modification')),
                ('datereforme', models.DateTimeField(auto_now=True, verbose_name='date de reforme')),
                ('appareil', models.ForeignKey(blank=True, help_text=' Appareil ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Appareil', to='imagerie.appareil')),
                ('appareiltype', models.ForeignKey(blank=True, help_text=' Appareiltype ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Appareiltype', to='imagerie.appareiltype')),
                ('etablissement', models.ForeignKey(blank=True, help_text=' Etablissement ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Etablissement', to='imagerie.etablissement')),
                ('localisation', models.ForeignKey(blank=True, help_text=' Localisation ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Localisation', to='imagerie.localisation')),
                ('marque', models.ForeignKey(blank=True, help_text=' Marque ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Marque', to='imagerie.marque')),
                ('vlanid', models.ForeignKey(blank=True, help_text=' Vlan ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Vlan', to='imagerie.vlan')),
            ],
            options={
                'db_table': 'Machine',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='modalite',
            name='machine',
            field=models.ForeignKey(blank=True, help_text=' Machine ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Machine', to='imagerie.machine'),
        ),
        migrations.AddField(
            model_name='serveur',
            name='machine',
            field=models.ForeignKey(blank=True, help_text=' Machine ', null=True, on_delete=django.db.models.deletion.PROTECT, to='imagerie.machine'),
        ),
    ]
