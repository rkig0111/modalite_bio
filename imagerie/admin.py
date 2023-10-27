from django.contrib import admin
from imagerie.models import Appareil, Etablissement, Localisation, Marque, Appareiltype, Vlan, Service, Machine
from imagerie.models import Modalite, Serveur, Testlan, Logiciel, Bdd, Ras, Resspartage, Identifiant, Projet


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class LogicielAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class BddAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class RasAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class ResspartageAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class IdentifiantAdmin(admin.ModelAdmin):
    list_display = ('login',)
    
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom',)
 
class VlanAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class LocalisationAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class EtablissementAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class MarqueAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class AppareilAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class AppareiltypeAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class ServeurAdmin(admin.ModelAdmin):
    list_display = ('projet', 'machine')
    
class TestlanAdmin(admin.ModelAdmin):
    list_display = ('modalite',)
    
class ModaliteAdmin(admin.ModelAdmin):
    list_display = ('aet', 'machine')

class MachineAdmin(admin.ModelAdmin):
    list_display = ('addrip', 'appareiltype')

# col = [addrip, aet, port, masque, hostname, modalite, hostname, systeme, macadresse, dicom, inventaire \
# remarque, appareil, etablissement, localisation, marque, typeappareil, vlan ]

admin.site.register(Vlan, VlanAdmin)
admin.site.register(Etablissement, EtablissementAdmin)
admin.site.register(Localisation, LocalisationAdmin)
admin.site.register(Marque, MarqueAdmin)
admin.site.register(Appareil, AppareilAdmin)
admin.site.register(Appareiltype, AppareiltypeAdmin)
admin.site.register(Serveur, ServeurAdmin)
admin.site.register(Testlan, TestlanAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Modalite, ModaliteAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Logiciel, LogicielAdmin)
admin.site.register(Bdd, BddAdmin)
admin.site.register(Ras, RasAdmin)
admin.site.register(Resspartage, ResspartageAdmin)
admin.site.register(Identifiant, IdentifiantAdmin)
admin.site.register(Projet, ProjetAdmin)