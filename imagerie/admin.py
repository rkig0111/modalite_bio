from django.contrib import admin
from imagerie.models import Appareil, Etablissement, Localisation, Marque, AppareilType, Vlan
from imagerie.models import Liste, Serveur, Connect

class VlanAdmin(admin.ModelAdmin):
    list_display = ('num', 'nom')

class LocalisationAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'tel')

class EtablissementAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class MarqueAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class AppareilAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class AppareilTypeAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class ServeurAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    
class ConnectAdmin(admin.ModelAdmin):
    list_display = ('liste',)
    
class ListeAdmin(admin.ModelAdmin):
    list_display = ('appareil', 'marque', 'addrip', 'aet', 'port', 'macadresse', 'localisation')

# col = [addrip, aet, port, masque, hostname, modalite, hostname, systeme, macadresse, dicom, inventaire \
# remarque, appareil, etablissement, localisation, marque, typeappareil, vlan ]

"""class RemarqueAdmin(admin.ModelAdmin):
    list_display = ('remarque',)   
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service', 'indexetablissement')
class ServeurNewAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ip', 'aet', 'port')
class StoreNewAdmin(admin.ModelAdmin):
    list_display = ('nom', 'aet', 'ip', 'port')
class WorklistNewAdmin(admin.ModelAdmin):
    list_display = ('nom', 'aet', 'ip', 'port')"""

admin.site.register(Vlan, VlanAdmin)
admin.site.register(Etablissement, EtablissementAdmin)
admin.site.register(Localisation, LocalisationAdmin)
admin.site.register(Marque, MarqueAdmin)
admin.site.register(Appareil, AppareilAdmin)
admin.site.register(AppareilType, AppareilTypeAdmin)
admin.site.register(Serveur, ServeurAdmin)
admin.site.register(Connect, ConnectAdmin)
admin.site.register(Liste, ListeAdmin)
"""admin.site.register(Service, ServiceAdmin)
admin.site.register(Remarque, RemarqueAdmin)
admin.site.register(Serveur, ServeurAdmin)
admin.site.register(WorklistNew, WorklistNewAdmin)
admin.site.register(Store, StoreAdmin)"""