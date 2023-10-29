from django import forms

from .models import Machine

class MachineForm(forms.ModelForm):

    class Meta:
        model = Machine
        fields = ("etablissement", "appareil", "appareiltype", "marque", "addrip", "vlan", "hostname", "systeme", "inventaire", "localisation", )
        # widgets = {'appareil ': Textarea(attrs ={'cols ':20,'rows ':3}) ,}