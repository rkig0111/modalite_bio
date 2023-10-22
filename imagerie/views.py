from django.http import Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from .models import Vlan, Appareil, Etablissement, Localisation, Marque, Appareiltype, Modalite, Serveur
# from smart_view.smart_fields import ConditionnalSmartField, ToolsSmartField
# from smart_view.smart_view import SmartView, ComputedSmartField
# view.smart_fields

def index(request):
    tables = ["Vlan", "Appareil", "Etablissement", "Localisation", "Marque", "Appareiltype", "Modalite", "Serveur"]
    return render(request, "imagerie/index.html", {"tables": tables})

def list_vlan(request):
    vlans = get_list_or_404(Vlan)
    return render(request, "imagerie/list_vlan.html", {"vlans": vlans, "modele": "vlan"})

def detail_vlan(request, vlan_id):
    vlan = get_object_or_404(Vlan, pk=vlan_id)
    return render(request, 'imagerie/detail_vlan.html', {'vlan': vlan})


def list_appareil(request):
    appareils = get_list_or_404(Appareil)
    return render(request, "imagerie/list_appareil.html", {"appareils": appareils, "modele": "appareil"})

def detail_appareil(request, appareil_id):
    appareil = get_object_or_404(Appareil, pk=appareil_id)
    return render(request, 'imagerie/detail_appareil.html', {'appareil': appareil})


def list_etablissement(request):
    etablissements = get_list_or_404(Etablissement)
    return render(request, "imagerie/list_etablissement.html", {"etablissements": etablissements, "modele": "etablissement"})

def detail_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
    return render(request, 'imagerie/detail_etablissement.html', {'etablissement': etablissement})


def list_localisation(request):
    localisations = get_list_or_404(Localisation)
    return render(request, "imagerie/list_localisation.html", {"localisations": localisations, "modele": "localisation"})

def detail_localisation(request, localisation_id):
    localisation = get_object_or_404(Localisation, pk=localisation_id)
    return render(request, 'imagerie/detail_localisation.html', {'localisation': localisation})


def list_marque(request):
    marques = get_list_or_404(Marque)
    return render(request, "imagerie/list_marque.html", {"marques": marques, "modele": "marque"})


def detail_marque(request, marque_id):
    marque = get_object_or_404(Marque, pk=marque_id)
    return render(request, 'imagerie/detail_marque.html', {'marque': marque})


def list_appareiltype(request):
    appareiltypes = get_list_or_404(Appareiltype)
    return render(request, "imagerie/list_appareiltype.html", {"appareiltypes": appareiltypes, "modele": "appareiltype"})

def detail_appareiltype(request, appareiltype_id):
    appareiltype = get_object_or_404(Appareiltype, pk=appareiltype_id)
    return render(request, 'imagerie/detail_appareiltype.html', {'appareiltype': appareiltype})


def list_modalite(request):
    modalites = get_list_or_404(Modalite)
    return render(request, "imagerie/list_modalite.html", {"modalites": modalites, "modele": "modalite"})

def detail_modalite(request, modalite_id):
    modalite = get_object_or_404(Modalite, pk=modalite_id)
    return render(request, 'imagerie/detail_modalite.html', {'modalite': modalite})


def list_serveur(request):
    serveurs = get_list_or_404(Serveur)
    return render(request, "imagerie/list_serveur.html", {"serveurs": serveurs, "modele": "serveur"})

def detail_serveur(request, serveur_id):
    serveur = get_object_or_404(Serveur, pk=serveur_id)
    print("---> serveur_id : ", serveur_id)
    print("---> serveur : ", serveur)
    return render(request, 'imagerie/detail_serveur.html', {'serveur': serveur})


"""def ping_modalite(request, modalite_id):
    return render(request, 'imagerie/ping_liste.html', {'liste': liste})"""