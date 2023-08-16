# Generated by Django 4.0 on 2023-08-16 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imagerie', '0002_alter_appareil_id_alter_appareiltype_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Liste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('addrip', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('aet', models.CharField(max_length=30)),
                ('port', models.IntegerField()),
                ('masque', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('modalite', models.CharField(max_length=2)),
                ('hostname', models.CharField(max_length=30)),
                ('systeme', models.CharField(max_length=30)),
                ('macadresse', models.CharField(blank=True, max_length=17, null=True)),
                ('dicom', models.CharField(blank=True, max_length=3, null=True)),
                ('inventaire', models.CharField(blank=True, max_length=24, null=True)),
                ('remarque', models.CharField(blank=True, max_length=1024, null=True)),
                ('appareil', models.ForeignKey(blank=True, help_text=' Appareil ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Appareil', to='imagerie.appareil')),
                ('appareiltype', models.ForeignKey(blank=True, help_text=' AppareilType ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='AppareilType', to='imagerie.appareiltype')),
                ('etablissement', models.ForeignKey(blank=True, help_text=' Etablissement ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Etablissement', to='imagerie.etablissement')),
                ('localisation', models.ForeignKey(blank=True, help_text=' Localisation ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Localisation', to='imagerie.localisation')),
                ('marque', models.ForeignKey(blank=True, help_text=' Marque ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Marque', to='imagerie.marque')),
                ('vlan', models.ForeignKey(blank=True, help_text=' Vlan ', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Vlan', to='imagerie.vlan')),
            ],
            options={
                'db_table': 'Liste',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Serveur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(blank=True, max_length=30, null=True)),
                ('aet', models.CharField(blank=True, max_length=30, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('masque', models.GenericIPAddressField(blank=True, default='0.0.0.0', null=True)),
                ('port', models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True)),
            ],
            options={
                'db_table': 'Serveur',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Connect',
            fields=[
                ('liste', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='imagerie.liste')),
                ('pingip', models.BooleanField(default=False)),
                ('pinghost', models.BooleanField(default=False)),
                ('pingdicom', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Connect',
                'managed': True,
            },
        ),
    ]