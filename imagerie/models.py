from django.db import models
from django.utils.translation import gettext as _
from django.db import models

class Appareil(models.Model):
    nom = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Appareil'

    def __str__(self):
        return "{0}".format(self.nom)


class Localisation(models.Model):
    code = models.CharField(blank=True, null=True, max_length=30) 
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
    nom = models.CharField(max_length=30, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Marque'

    def __str__(self):
        return "{0}".format(self.nom)


class Appareiltype(models.Model):
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


class Etablissement(models.Model):
    nom = models.CharField(max_length=45, blank=True, null=True)
    site = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Etablissement'

    def __str__(self):
        return "{0}".format(self.nom)


class Service(models.Model):
    nom = models.CharField(max_length=45, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')

    class Meta:
        managed = True
        db_table = 'Service'

    def __str__(self):
        return "{0}".format(self.nom)
    
    
class Modalite(models.Model):
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

    appareilid = models.ForeignKey('Appareil', null=True, blank=True, on_delete=models.PROTECT, related_name='Appareil', help_text=_(" Appareil "), )
    marqueid = models.ForeignKey('Marque', null=True, blank=True, on_delete=models.PROTECT, related_name='Marque', help_text=_(" Marque "), )  
    appareiltypeid = models.ForeignKey('Appareiltype', null=True, blank=True, on_delete=models.PROTECT, related_name='Appareiltype', help_text=_(" Appareiltype "), ) 
    etablissementid = models.ForeignKey('Etablissement', null=True, blank=True, on_delete=models.PROTECT, related_name='Etablissement', help_text=_(" Etablissement "), ) 
    service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.PROTECT, related_name='Service', help_text=_(" Service "), )
    srvdicom = models.BooleanField(default=False)
    modalite = models.CharField(max_length=2, blank=True, null=True) 
    addrip = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    mask = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    passerelle = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    aet = models.CharField(max_length=30, blank=True, null=True)    
    port = models.IntegerField()  
    hostname = models.CharField(max_length=30, blank=True, null=True) 
    macadresse = models.CharField(max_length=17, blank=True, null=True) 
    vlanid = models.ForeignKey('Vlan', null=True, blank=True, on_delete=models.PROTECT, related_name='Vlan', help_text=_(" Vlan "), ) 
    pacs = models.ManyToManyField('self', blank=True)
    worklist = models.ManyToManyField('self', blank=True)
    store = models.ManyToManyField('self', blank=True)
    serveurid = models.ForeignKey('Serveur', null=True, blank=True, on_delete=models.PROTECT, related_name='Serveur', help_text=_(" Serveur "), ) 
    localisationid = models.ForeignKey('Localisation', null=True, blank=True, on_delete=models.PROTECT, related_name='Localisation', help_text=_(" Localisation "), ) 
    systeme = models.CharField(max_length=30, blank=True, null=True)  
    inventaire = models.CharField(max_length=24, blank=True, null=True) 
    divers = models.CharField(max_length=1024, blank=True, null=True) 
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')  
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme')  

    class Meta:
        managed = True
        db_table = 'Modalite'

    def __str__(self):
        return "{0} {1}".format(self.aet, self.addrip)


class Logiciel(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    version = models.CharField(max_length=30, blank=True, null=True)
    editeur = models.CharField(max_length=30, blank=True, null=True)
    contact = models.CharField(max_length=30, blank=True, null=True)
    tel = models.CharField(max_length=30, blank=True, null=True)
    referent = models.CharField(max_length=30, blank=True, null=True)
    marche = models.CharField(max_length=30, blank=True, null=True)
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme')  

    class Meta:
        managed = True
        db_table = 'Logiciel'

    def __str__(self):
        return "{0}  {1}".format(self.nom)
    
    
class Bdd(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    identif = models.CharField(blank=True, null=True, max_length=30) 
    password = models.CharField(blank=True, null=True, max_length=30) 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Bdd'

    def __str__(self):
        return "{0}  {1}".format(self.nom)    
    

class Ras(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    prenom = models.CharField(blank=True, null=True, max_length=30) 
    mail = models.CharField(blank=True, null=True, max_length=50) 
    tel = models.CharField(blank=True, null=True, max_length=30) 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Ras'

    def __str__(self):
        return "{0}  {1}".format(self.nom)     


class Resspartage(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    identif = models.CharField(blank=True, null=True, max_length=30) 
    password = models.CharField(blank=True, null=True, max_length=30) 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Resspartage'

    def __str__(self):
        return "{0}  {1}".format(self.nom)    
    

class Compte(models.Model):
    login = models.CharField(blank=True, null=True, max_length=30) 
    password = models.CharField(blank=True, null=True, max_length=30) 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Compte'

    def __str__(self):
        return "{0}  {1}".format(self.nom)   
    
    
class Projet(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Service "), )  # related_name='Service', 
    editeur = models.CharField(max_length=50, blank=True, null=True)
    logicielid = models.ForeignKey('Logiciel', null=True, blank=True, on_delete=models.PROTECT, related_name='Logiciel', help_text=_(" Logiciel "), )
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme')  

    class Meta:
        managed = True
        db_table = 'Projet'

    def __str__(self):
        return "{0}  {1}".format(self.nom)


class Serveur(models.Model):
    appareilid = models.ForeignKey('Appareil', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Appareil "), )  # related_name='Appareil', 
    marqueid = models.ForeignKey('Marque', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Marque "), )  # related_name='Marque', 
    appareiltypeid = models.ForeignKey('Appareiltype', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Appareiltype "), )  # related_name='Appareiltype', 
    etablissementid = models.ForeignKey('Etablissement', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Etablissement "), )  # related_name='Etablissement', 
    srvdicom = models.BooleanField(default=False)
    modalite = models.CharField(max_length=2, blank=True, null=True)     
    hostname = models.CharField(max_length=30, blank=True, null=True)  
    addrip = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)    # VM / PHYSIQUE
    editeur = models.CharField(max_length=30, blank=True, null=True) 
    projetid = models.ForeignKey('Projet', null=True, blank=True, on_delete=models.PROTECT, related_name='Projet', help_text=_(" Projet "), )
    vlanid = models.ForeignKey('Vlan', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Vlan "), )  # related_name='Vlan', 
    localisationid = models.ForeignKey('Localisation', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Localisation "), )  # related_name='Localisation', 
    ram = models.CharField(max_length=10, blank=True, null=True) 
    cores =  models.IntegerField()  
    ddsystem = models.CharField(max_length=10, blank=True, null=True) 
    dddata = models.CharField(max_length=10, blank=True, null=True) 
    os = models.CharField(max_length=30, blank=True, null=True)
    bddid = models.ForeignKey('Bdd', null=True, blank=True, on_delete=models.PROTECT, related_name='Bdd', help_text=_(" Base de données "), )
    rasid = models.ForeignKey('Ras', null=True, blank=True, on_delete=models.PROTECT, related_name='Ras', help_text=_(" compte ras_xxx "), )
    comptesid = models.ForeignKey('Compte', null=True, blank=True, on_delete=models.PROTECT, related_name='Compte', help_text=_(" Compte "), )
    resspartageid = models.ForeignKey('Resspartage', null=True, blank=True, on_delete=models.PROTECT, related_name='Resspartage', help_text=_(" Ressource partagée "), )
    systeme = models.CharField(max_length=30, blank=True, null=True)  
    inventaire = models.CharField(max_length=24, blank=True, null=True) 
    divers = models.CharField(max_length=1024, blank=True, null=True) 
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')  
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme')  

    class Meta:
        managed = True
        db_table = 'Serveur'

    def __str__(self):
        return "{0} {1}".format(self.hostname)

    
class Testlan(models.Model):
    modalite = models.OneToOneField(Modalite, on_delete=models.CASCADE, primary_key=True,)
    pingip = models.BooleanField(default=False)
    pinghost = models.BooleanField(default=False)
    pingdicom = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'Testlan'

    def __str__(self):
        return "IP de la modalité : {0},   aet : {1}".format(self.modalite.addrip, self.modalite.aet)

