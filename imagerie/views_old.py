from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from .models import Vlan, Machine, Appareil, Etablissement, Localisation, Marque, Appareiltype, Modalite, Serveur
from .forms import VlanForm, MachineForm, AppareilForm, EtablissementForm, LocalisationForm,  MarqueForm, AppareiltypeForm, ModaliteForm, ServeurForm
from django.forms import ModelForm, Textarea
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
# from smart_view.smart_fields import ConditionnalSmartField, ToolsSmartField
# from smart_view.smart_view import SmartView, ComputedSmartField
# view.smart_fields

from django import forms
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms. widgets import RadioSelect , CheckboxSelectMultiple
from django.forms. widgets import SelectDateWidget


"""def machine(request):
    # on instancie un formulaire
    form = MachineForm()
    context = {"form" : form ,}
    return render(request ,'imagerie/detail_machine.html', context )"""
      
"""      # on teste si on est bien en validation de formulaire (POST)
      print("request.method ----> ", request.method )
      if request.method == "POST":
          # Si oui on récupère les données postées
          form = MachineForm(request.POST)
          # on vérifie la validit é du formulaire
          if form.is_valid():
              nouvelle_machine = form.save()
              # on prépare un nouveau message
              # messages.success(request ,'Nouvelle machine'+ nouvelle_machine.appareil+' '+ nouvelle_machine.appareiltype)
              #return redirect ( reverse ('detail ', args =[ new_contact .pk] ))
              context = {'pers ': nouvelle_machine }
      # Si méthode GET , on présente le formulaire
      context = {'machine ': form}
      return render(request ,'imagerie/detail_machine.html', context )
"""  
  
User = get_user_model()


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")  
        password = request.POST.get("password")         
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'imagerie/signup.html')  


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")  
        password = request.POST.get("password")         
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
    return render(request, 'imagerie/login.html')   


def logout_user(request):
    logout(request)
    return redirect('index')   


def toindex(request):
    return redirect("index")

     
def index(request):
    tables = ["Vlan", "Appareil", "Etablissement", "Localisation", "Marque", "Appareiltype", "Modalite", "Serveur", "Machine"]
    return render(request, "imagerie/index.html", {"tables": tables})


# def index(request):
#     tables = []
#     return render(request, "imagerie/base.html", {"tables": tables})

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


def list_machine(request):
    machines = get_list_or_404(Machine)
    return render(request, "imagerie/list_machine.html", {"machines": machines, "modele": "machine"})


def detail_machine(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    return render(request, 'imagerie/detail_machine.html', {'machine': machine})


def machine_new(request):
    if request.method == "POST":
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            # machine.author = request.user
            # machine.published_date = timezone.now()
            machine.save()
            return redirect('detail_machine', machine.id)
    else:
        form = MachineForm()
    return render(request, 'imagerie/edit_machine.html', {'form': form})


def edit_machine(request, id):
    machine = get_object_or_404(Machine, id=id)
    print("machine ---> ", machine)
    if request.method == "POST":
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            machine = form.save(commit=False)
            # machine.author = request.user
            # machine.published_date = timezone.now()
            machine.save()
            # return redirect('detail_machine', machine.id)
            return redirect('index')
    else:
        form = MachineForm(instance=machine)
    return render(request, 'imagerie/edit_machine.html', {'form': form})


def edit_appareil(request, id):
    appareil = get_object_or_404(Appareil, id=id)
    print("appareil ---> ", appareil)
    if request.method == "POST":
        form = AppareilForm(request.POST, instance=appareil)
        if form.is_valid():
            appareil = form.save(commit=False)
            # appareil.author = request.user
            # appareil.published_date = timezone.now()
            appareil.save()
            # return redirect('detail_appareil', appareil.id)
            return redirect('index')
    else:
        form = AppareilForm(instance=appareil)
    return render(request, 'imagerie/edit_appareil.html', {'form': form})


def edit_etablissement(request, id):
    etablissement = get_object_or_404(Etablissement, id=id)
    print("etablissement ---> ", etablissement)
    if request.method == "POST":
        form = EtablissementForm(request.POST, instance=etablissement)
        if form.is_valid():
            etablissement = form.save(commit=False)
            # etablissement.author = request.user
            # etablissement.published_date = timezone.now()
            etablissement.save()
            # return redirect('detail_etablissement', etablissement.id)
            return redirect('index')
    else:
        form = EtablissementForm(instance=etablissement)
    return render(request, 'imagerie/edit_etablissementhtml', {'form': form})


def edit_localisation(request, id):
    localisation = get_object_or_404(Localisation, id=id)
    print("localisation ---> ", localisation)
    if request.method == "POST":
        form = LocalisationForm(request.POST, instance=localisation)
        if form.is_valid():
            localisation = form.save(commit=False)
            # localisation.author = request.user
            # localisation.published_date = timezone.now()
            localisation.save()
            # return redirect('detail_localisation', localisation.id)
            return redirect('index')
    else:
        form = LocalisationForm(instance=localisation)
    return render(request, 'imagerie/edit_localisation.html', {'form': form})


def edit_marque(request, id):
    marque = get_object_or_404(Marque, id=id)
    print("marque ---> ", marque)
    if request.method == "POST":
        form = MarqueForm(request.POST, instance=marque)
        if form.is_valid():
            marque = form.save(commit=False)
            # marque.author = request.user
            # marque.published_date = timezone.now()
            marque.save()
            # return redirect('detail_marque', marque.id)
            return redirect('index')
    else:
        form = MarqueForm(instance=marque)
    return render(request, 'imagerie/edit_marque.html', {'form': form})


def edit_appareiltype(request, id):
    appareiltype = get_object_or_404(Appareiltype, id=id)
    print("appareiltype ---> ", appareiltype)
    if request.method == "POST":
        form = AppareiltypeForm(request.POST, instance=appareiltype)
        if form.is_valid():
            appareiltype = form.save(commit=False)
            # appareiltype.author = request.user
            # appareiltype.published_date = timezone.now()
            appareiltype.save()
            # return redirect('detail_appareiltype', appareiltype.id)
            return redirect('index')
    else:
        form = AppareiltypeForm(instance=appareiltype)
    return render(request, 'imagerie/edit_appareiltype.html', {'form': form})


def edit_modalite(request, id):
    modalite = get_object_or_404(Modalite, id=id)
    print("modalite ---> ", modalite)
    if request.method == "POST":
        form = ModaliteForm(request.POST, instance=modalite)
        if form.is_valid():
            modalite = form.save(commit=False)
            # modalite.author = request.user
            # modalite.published_date = timezone.now()
            modalite.save()
            # return redirect('detail_modalite', modalite.id)
            return redirect('index')
    else:
        form = ModaliteForm(instance=modalite)
    return render(request, 'imagerie/edit_modalite.html', {'form': form})


def edit_serveur(request, id):
    serveur = get_object_or_404(Serveur, id=id)
    print("serveur ---> ", serveur)
    if request.method == "POST":
        form = ServeurForm(request.POST, instance=serveur)
        if form.is_valid():
            serveur = form.save(commit=False)
            # serveur.author = request.user
            # serveur.published_date = timezone.now()
            serveur.save()
            # return redirect('detail_serveur', serveur.id)
            return redirect('index')
    else:
        form = ServeurForm(instance=serveur)
    return render(request, 'imagerie/edit_serveur.html', {'form': form})


def edit_vlan(request, id):
    vlan = get_object_or_404(Vlan, id=id)
    print("vlan ---> ", vlan)
    if request.method == "POST":
        form = VlanForm(request.POST, instance=vlan)
        if form.is_valid():
            vlan = form.save(commit=False)
            # vlan.author = request.user
            # vlan.published_date = timezone.now()
            vlan.save()
            # return redirect('detail_vlan', vlan.id)
            return redirect('index')
    else:
        form = VlanForm(instance=vlan)
    return render(request, 'imagerie/edit_vlan.html', {'form': form})


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