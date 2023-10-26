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
        return "{0} ".format(self.nom)
    
    
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
        return "{0} ".format(self.nom)    
    

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
        return "{0} ".format(self.nom)     


class Resspartage(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    identif = models.CharField(blank=True, null=True, max_length=30) 
    password = models.CharField(blank=True, null=True, max_length=30, default="voir TeamPass") 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Resspartage'

    def __str__(self):
        return "{0} ".format(self.nom)    
    

class Identifiant(models.Model):
    login = models.CharField(blank=True, null=True, max_length=30) 
    password = models.CharField(blank=True, null=True, max_length=30, default="voir TeamPass") 
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')    

    class Meta:
        managed = True
        db_table = 'Compte'

    def __str__(self):
        return "{0}".format(self.login)   
    
    
class Projet(models.Model):
    nom = models.CharField(blank=True, null=True, max_length=30) 
    service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Service "), )  # related_name='Service', 
    editeur = models.CharField(max_length=50, blank=True, null=True)
    logiciel = models.ForeignKey('Logiciel', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Logiciel "), )  # , related_name='Logiciel'
    divers = models.CharField(max_length=255, blank=True, null=True)
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme')  

    class Meta:
        managed = True
        db_table = 'Projet'

    def __str__(self):
        return "{0}".format(self.nom)

class Machine(models.Model):    
    etablissement = models.ForeignKey('Etablissement', null=True, blank=True, on_delete=models.PROTECT, related_name='Etablissement', help_text=_(" Etablissement "), )
    appareil = models.ForeignKey('Appareil', null=True, blank=True, on_delete=models.PROTECT, related_name='Appareil', help_text=_(" Appareil "), )     
    appareiltype = models.ForeignKey('Appareiltype', null=True, blank=True, on_delete=models.PROTECT, related_name='Appareiltype', help_text=_(" Appareiltype "), ) 
    marque = models.ForeignKey('Marque', null=True, blank=True, on_delete=models.PROTECT, related_name='Marque', help_text=_(" Marque "), ) 
    addrip = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    vlan = models.ForeignKey('Vlan', null=True, blank=True, on_delete=models.PROTECT, related_name='Vlan', help_text=_(" Vlan "), ) 
    hostname = models.CharField(max_length=30, blank=True, null=True) 
    systeme = models.CharField(max_length=30, blank=True, null=True)  
    inventaire = models.CharField(max_length=24, blank=True, null=True)
    localisation = models.ForeignKey('Localisation', null=True, blank=True, on_delete=models.PROTECT, related_name='Localisation', help_text=_(" Localisation "), )
    datecreat = models.DateTimeField(auto_now_add=True, verbose_name='date de création')
    datemodif = models.DateTimeField(auto_now=True, verbose_name='date de modification')  
    datereforme = models.DateTimeField(auto_now=True, verbose_name='date de reforme') 

    class Meta:
        managed = True
        db_table = 'Machine'
        ordering = ["addrip"]

    def __str__(self):
        return "{0}".format(self.addrip)

    
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

    machine = models.ForeignKey('Machine', null=True, blank=True, on_delete=models.PROTECT, related_name='Machine', help_text=_(" Machine ") )
    service = models.ForeignKey('Service', null=True, blank=True, on_delete=models.PROTECT, related_name='Service', help_text=_(" Service ") )
    srvdicom = models.BooleanField(default=False)
    modalite = models.CharField(max_length=2, blank=True, null=True) 
    mask = models.GenericIPAddressField(default="255.255.255.0", blank=True, null=True)
    passerelle = models.GenericIPAddressField(default="0.0.0.1", blank=True, null=True)
    aet = models.CharField(max_length=30, blank=True, null=True)    
    port = models.IntegerField()  
    macadresse = models.CharField(max_length=17, blank=True, null=True) 
    # pacs = models.ManyToManyField('self', blank=True)
    pacs = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='Pacs',help_text=_(" Pacs ") )  
    # worklist = models.ManyToManyField('self', blank=True)
    worklist = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='Worklist',help_text=_(" Worklist ") )
    store = models.ManyToManyField('self', blank=True)
    serveur = models.ForeignKey('Serveur', null=True, blank=True, on_delete=models.PROTECT, related_name='Serveur', help_text=_(" Serveur ") ) 
    divers = models.CharField(max_length=1024, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'Modalite'
        ordering = ["aet"]

    def __str__(self):
        return "{0} {1}".format(self.aet, Machine.addrip)


class Serveur(models.Model):
    machine = models.ForeignKey('Machine', null=True, blank=True, on_delete=models.PROTECT, help_text=_(" Machine "), )   # related_name='Machine', 
    # srvdicom = models.BooleanField(default=False)
    # modalite = models.CharField(max_length=2, blank=True, null=True)     
    type = models.CharField(max_length=30, blank=True, null=True, default="VM", help_text=_(" VM / Physique "),)    # VM / PHYSIQUE
    editeur = models.CharField(max_length=30, blank=True, null=True) 
    projet = models.ForeignKey('Projet', null=True, blank=True, on_delete=models.PROTECT, related_name='Projet', help_text=_(" Projet "), )
    ram = models.CharField(max_length=10, blank=True, null=True) 
    cores =  models.IntegerField(blank=True, null=True)  
    ddsystem = models.CharField(max_length=10, blank=True, null=True) 
    dddata = models.CharField(max_length=10, blank=True, null=True) 
    os = models.CharField(max_length=30, blank=True, null=True)
    bdd = models.ForeignKey('Bdd', null=True, blank=True, on_delete=models.PROTECT, related_name='Bdd', help_text=_(" Base de données "), )
    ras = models.ForeignKey('Ras', null=True, blank=True, on_delete=models.PROTECT, related_name='Ras', help_text=_(" compte ras_xxx "), )
    identifiant = models.ManyToManyField('Identifiant', help_text=_(" Identifiant "), )
    resspartage = models.ForeignKey('Resspartage', null=True, blank=True, on_delete=models.PROTECT, related_name='Resspartage', help_text=_(" Ressource partagée "), )
    divers = models.CharField(max_length=1024, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'Serveur'
        ordering = ["projet"]

    def __str__(self):
        return "{0}".format(self.projet)

    
class Testlan(models.Model):
    modalite = models.OneToOneField(Modalite, on_delete=models.CASCADE, primary_key=True,)
    pingip = models.BooleanField(default=False)
    pinghost = models.BooleanField(default=False)
    pingdicom = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'Testlan'

    def __str__(self):
        return "IP de la modalité : {0}".format(self.modalite.aet)

