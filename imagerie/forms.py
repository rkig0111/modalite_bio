from django import forms

from .models import Machine, Appareil, Etablissement, Localisation, Marque, Appareiltype, Modalite, Serveur, Vlan


class MachineForm(forms.ModelForm):

    class Meta:
        model = Machine
        fields = ("etablissement", "appareil", "appareiltype", "marque", "addrip", "vlan", "hostname", "systeme", "inventaire", "localisation", "datereforme",)
        # widgets = {'appareil ': Textarea(attrs ={'cols ':20,'rows ':3}) ,}
        

class AppareilForm(forms.ModelForm):

    class Meta:
        model = Appareil
        fields = ("nom", "divers", )
        

class EtablissementForm(forms.ModelForm):
    
    class Meta:
        model = Etablissement
        fields = ("nom", "site", "divers", )
        
        
class LocalisationForm(forms.ModelForm):
    
    class Meta:
        model = Localisation
        fields = ("code", "nomutil", "tel", "divers", )
    
        
class MarqueForm(forms.ModelForm):
    
    class Meta:
        model = Marque
        fields = ("nom", "divers", )    
                
    
class AppareiltypeForm(forms.ModelForm):
    
    class Meta:
        model = Appareil
        fields = ("nom", "divers", )   
        
    
class ModaliteForm(forms.ModelForm):
    
    class Meta:
        model = Modalite
        fields = ("machine", "service", "srvdicom", "modalite", "mask", "passerelle", "aet", "port", "macadresse", "pacs", "worklist", "store", "serveur", "divers", "modedegrade", "doc",)    


class ServeurForm(forms.ModelForm):
    
    class Meta:
        model = Serveur
        fields = ("machine", "type", "editeur", "projet", "ram", "cores", "ddsystem", "dddata", "os", "bdd", "ras", "identifiant", "resspartage", "divers", )    
        

class VlanForm(forms.ModelForm):
    
    class Meta:
        model = Vlan
        fields = ("num", "nom", "divers", )    
