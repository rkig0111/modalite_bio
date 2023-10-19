from django.db import models
from django.utils.translation import gettext as _

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `# managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Appareil(models.Model):
    # id = models.IntegerField(db_column='Index', primary_key=True) 
    nom = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Appareil'

    def __str__(self):
        return "{0}".format(self.nom)


class Etablissement(models.Model):
    # id = models.IntegerField(db_column='Index', primary_key=True, auto) 
    nom = models.CharField(max_length=30, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Etablissement'

    def __str__(self):
        return "{0}".format(self.nom)


class Localisation(models.Model):
    # id = models.AutoField(db_column='Index', primary_key=True) 
    code = models.CharField(unique=True, max_length=30) 
    nom = models.CharField(blank=True, null=True, max_length=30)  
    nomutil = models.CharField(blank=True, null=True, max_length=30)  
    tel = models.CharField(blank=True, null=True, max_length=30) 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Localisation'

    def __str__(self):
        return "{0}  {1}".format(self.code, self.nom)


class Marque(models.Model):
    # id = models.IntegerField(db_column='Index', primary_key=True) 
    nom = models.CharField(max_length=30, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Marque'

    def __str__(self):
        return "{0}".format(self.nom)


class AppareilType(models.Model):
    # id = models.IntegerField(db_column='Index', primary_key=True) 
    nom = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'AppareilType'

    def __str__(self):
        return "{0}".format(self.nom)    


class Vlan(models.Model):
    # id = models.IntegerField(primary_key=True)
    num = models.IntegerField(unique=True, blank=True, null=True)
    nom = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Vlan'

    def __str__(self):
        return "{0}".format(self.nom)

     
class Serveur(models.Model):
    # id = models.IntegerField(db_column='Index', primary_key=True) 
    nom = models.CharField(max_length=30, blank=True, null=True) 
    aet = models.CharField(max_length=30, blank=True, null=True) 
    ip = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)  
    masque = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)  
    port = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'Serveur'

    def __str__(self):
        return "{0}".format(self.nom)

    
class Liste(models.Model):
    NA = 0
    PACS = 1
    WL = 2
    DACS = 3
    STORE = 4
    PRINT = 5
    OTHER = 6
    
    SERVEUR = (
        ('0', 'N/A'),
        ('1', 'PACS'),
        ('2', 'WL'),
        ('3', 'DACS'),
        ('4', 'STORE'),
        ('5', 'PRINT'),
        ('6', 'OTHER'),
    )
    
    # id = models.AutoField(db_column='Index', primary_key=True)
    serveur = models.BooleanField(default=False)
    # typeserveur = models.ManyToManyField('self', null=True, blank=True, choices=SERVEUR, default=NA)
    connexion = models.ManyToManyField('self', blank=True)
    addrip = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    aet = models.CharField(max_length=30, blank=True, null=True)    
    port = models.IntegerField()  
    masque = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    hostname = models.CharField(max_length=30, blank=True, null=True) 
    modalite = models.CharField(max_length=2, blank=True, null=True)  
    hostname = models.CharField(max_length=30, blank=True, null=True)
    systeme = models.CharField(max_length=30, blank=True, null=True)  
    macadresse = models.CharField(max_length=17, blank=True, null=True)    
    dicom = models.CharField(max_length=3, blank=True, null=True)
    inventaire = models.CharField(max_length=24, blank=True, null=True)     
    remarque = models.CharField(max_length=1024, blank=True, null=True)       
    appareil = models.ForeignKey('Appareil', null=True, blank=True, on_delete=models.PROTECT, related_name='Appareil', help_text=_(" Appareil "), )
    etablissement = models.ForeignKey('Etablissement', null=True, blank=True, on_delete=models.PROTECT, related_name='Etablissement', help_text=_(" Etablissement "), )
    localisation = models.ForeignKey('Localisation', null=True, blank=True, on_delete=models.PROTECT, related_name='Localisation', help_text=_(" Localisation "), )
    marque = models.ForeignKey('Marque', null=True, blank=True, on_delete=models.PROTECT, related_name='Marque', help_text=_(" Marque "), )
    appareiltype = models.ForeignKey('AppareilType', null=True, blank=True, on_delete=models.PROTECT, related_name='AppareilType', help_text=_(" AppareilType "), )
    vlan = models.ForeignKey('Vlan', null=True, blank=True, on_delete=models.PROTECT, related_name='Vlan', help_text=_(" Vlan "), )
    
    # dhcp = models.CharField(db_column='DHCP', max_length=2, blank=True, null=True)
    # pacs = models.CharField(db_column='Pacs', max_length=30)   
    # Service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.PROTECT, related_name='', help_text=_(" Service "), )
    # Serveur = models.ForeignKey('Serveur', null=True, blank=True, on_delete=models.PROTECT, related_name='', help_text=_(" Serveur "), )
    # Store = models.ForeignKey('Store', null=True, blank=True, on_delete=models.PROTECT, related_name='', help_text=_(" Store "), )
    # Worklist = models.ForeignKey('Worklist', null=True, blank=True, on_delete=models.PROTECT, related_name='', help_text=_(" Worklist "), )  
    # connect = models.ForeignKey('connect', null=True, blank=True, on_delete=models.PROTECT, related_name='connect', help_text=_("tests de connexions"), ) 

    # pinghost = models.CharField(db_column='PingHost', max_length=2)
    # ping = models.CharField(db_column='Ping', max_length=2)  
    # telnet = models.CharField(db_column='Telnet', max_length=2)
    # ping_echo = models.CharField(db_column='Ping Echo', max_length=2)
    # echo_modalite = models.CharField(db_column='Echo Modalite', max_length=2)
    # echostore = models.CharField(db_column='EchoStore', max_length=2)
    # echoworklist = models.CharField(db_column='EchoWorklist', max_length=2)
    # routage = models.CharField(db_column='Routage', max_length=30)

    # worklist = models.CharField(db_column='Worklist', max_length=30
    # vlan = models.CharField(db_column='Vlan', max_length=8, blank=True, null=True) 
    # type_machine = models.CharField(db_column='Type Machine', max_length=30)
    # store = models.CharField(db_column='Store', max_length=30, blank=True, null=True)    
    # remarque = models.CharField(db_column='Remarque', max_length=255)
    # marque = models.CharField(db_column='Marque', max_length=30)
    # localisation = models.CharField(db_column='Localisation', max_length=30)      
    # appareil = models.CharField(db_column='Appareil', max_length=30) 

    class Meta:
        managed = True
        db_table = 'Liste'

    def __str__(self):
        return "{0} {1}".format(self.aet, self.addrip)

    
class Testlan(models.Model):
    liste = models.OneToOneField(Liste, on_delete=models.CASCADE, primary_key=True,)
    pingip = models.BooleanField(default=False)
    pinghost = models.BooleanField(default=False)
    pingdicom = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'Testlan'

    def __str__(self):
        return "IP de la modalité : {0},   aet : {1}".format(self.liste.addrip, self.liste.aet)


"""class Service(models.Model):
    id = models.IntegerField(db_column='Index', primary_key=True)  
    service = models.CharField(db_column='Service', unique=True, max_length=30, blank=True, null=True) 
    indexetablissement = models.IntegerField(db_column='IndexEtablissement', blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'service'

    def __str__(self):
        return "{0}".format(self.service)"""

"""class Store(models.Model):
    id = models.IntegerField(db_column='idStore', primary_key=True) 
    nom = models.CharField(db_column='Nom', max_length=30, blank=True, null=True) 
    ip = models.DecimalField(db_column='IP', max_digits=12, decimal_places=0, blank=True, null=True) 
    port = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    aet = models.CharField(db_column='Aet', max_length=30, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'store'

    def __str__(self):
        return "{0}".format(self.nom)"""



"""class Worklist(models.Model):
    id = models.IntegerField(db_column='Index', primary_key=True) 
    nom = models.CharField(db_column='Nom', max_length=30, blank=True, null=True) 
    aet = models.CharField(db_column='Aet', max_length=30, blank=True, null=True)  
    ip = models.DecimalField(db_column='IP', max_digits=12, decimal_places=0, blank=True, null=True) 
    port = models.DecimalField(db_column='Port', max_digits=5, decimal_places=0, blank=True, null=True)
    masque = models.DecimalField(db_column='Masque', max_digits=12, decimal_places=0, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'worklist'

    def __str__(self):
        return "{0}".format(self.nom)"""
