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

from django.core.mail import send_mail
from modalite_bio.settings import EMAIL_HOST_USER
# , EMAIL_HOST_PASSWORD

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


def list_vlan(request):
    vlans = get_list_or_404(Vlan)
    return render(request, "imagerie/list_vlan.html", {"vlans": vlans, "modele": "vlan"})

def list_appareil(request):
    appareils = get_list_or_404(Appareil)
    # return render(request, "imagerie/list_appareil.html", {"appareils": appareils, "modele": "appareil"})
    return render(request, "imagerie/list_appareil.html", {"appareils": appareils})

def list_machine(request):
    machines = get_list_or_404(Machine)
    return render(request, "imagerie/list_machine.html", {"machines": machines})

"""def detail_appareil(request, appareil_id):
    appareil = get_object_or_404(Appareil, pk=appareil_id)
    return render(request, 'imagerie/detail_appareil.html', {'appareil': appareil})"""

def detail_appareil(request, id):
    appareil = get_object_or_404(Appareil, pk=id)
    return render(request, 'imagerie/detail_appareil.html', {'appareil': appareil})

def detail_machine(request, id):
    machine = get_object_or_404(Machine, pk=id)
    return render(request, 'imagerie/detail_machine.html', {'machine': machine})

def detail_modalite(request, id):
    modalite = get_object_or_404(Modalite, pk=id)
    return render(request, 'imagerie/detail_modalite.html', {'modalite': modalite})

def list_etablissement(request):
    etablissements = get_list_or_404(Etablissement)
    return render(request, "imagerie/list_etablissement.html", {"etablissements": etablissements, "modele": "etablissement"})

def list_localisation(request):
    localisations = get_list_or_404(Localisation)
    return render(request, "imagerie/list_localisation.html", {"localisations": localisations, "modele": "localisation"})

def list_marque(request):
    marques = get_list_or_404(Marque)
    return render(request, "imagerie/list_marque.html", {"marques": marques, "modele": "marque"})

def list_appareiltype(request):
    appareiltypes = get_list_or_404(Appareiltype)
    return render(request, "imagerie/list_appareiltype.html", {"appareiltypes": appareiltypes, "modele": "appareiltype"})

def list_modalite(request):
    modalites = get_list_or_404(Modalite)
    return render(request, "imagerie/list_modalite.html", {"modalites": modalites, "modele": "modalite"})

def list_serveur(request):
    serveurs = get_list_or_404(Serveur)
    return render(request, "imagerie/list_serveur.html", {"serveurs": serveurs, "modele": "serveur"})


"""def ping_modalite(request, modalite_id):
    return render(request, 'imagerie/ping_liste.html', {'liste': liste})"""


def edit_appareil(request, id):
    appareil = get_object_or_404(Appareil, id=id)
    print("appareil ---> ", appareil)
    print('La méthode de requête est : ', request.method)
    print('Les données POST sont : ', request.POST)
    if request.method == "POST":
        form = AppareilForm(request.POST, instance=appareil)
        if form.is_valid():
        #     send_mail(
        #     subject=f'Message from {form.cleaned_data["nom"] or "anonyme"} par modalit_bio',
        #     message=form.cleaned_data['nom'],
        #     from_email=EMAIL_HOST_USER,  
        #     recipient_list=[EMAIL_HOST_USER],
        # )
            appareil = form.save(commit=False)
            # appareil.author = request.user
            # appareil.published_date = timezone.now()
            appareil.save()
            # return redirect('detail_appareil', appareil.id)
            return redirect('index')
    else:
        form = AppareilForm(instance=appareil)
        # form =AppareilForm()
    return render(request, 'imagerie/edit_appareil.html', {'form': form})
    print(request)

def edit_machine(request, id):
    machine = get_object_or_404(Machine, id=id)
    print("machine ---> ", machine)
    print('La méthode de requête est : ', request.method)
    print('Les données POST sont : ', request.POST)
    if request.method == "POST":
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
        #     send_mail(
        #     subject=f'Message from {form.cleaned_data["nom"] or "anonyme"} par modalit_bio',
        #     message=form.cleaned_data['nom'],
        #     from_email=EMAIL_HOST_USER,  
        #     recipient_list=[EMAIL_HOST_USER],
        # )
            machine = form.save(commit=False)
            # appareil.author = request.user
            # appareil.published_date = timezone.now()
            machine.save()
            # return redirect('detail_machine', machine.id)
            return redirect('index')
    else:
        form = MachineForm(instance=machine)
        # form =MachineForm()
    return render(request, 'imagerie/edit_machine.html', {'form': form})
    print(request)


def edit_modalite(request, id):
    modalite = get_object_or_404(Modalite, id=id)
    print("modalite ---> ", modalite)
    print('La méthode de requête est : ', request.method)
    print('Les données POST sont : ', request.POST)
    if request.method == "POST":
        form = ModaliteForm(request.POST, instance=modalite)
        if form.is_valid():
        #     send_mail(
        #     subject=f'Message from {form.cleaned_data["nom"] or "anonyme"} par modalit_bio',
        #     message=form.cleaned_data['nom'],
        #     from_email=EMAIL_HOST_USER,  
        #     recipient_list=[EMAIL_HOST_USER],
        # )
            modalite = form.save(commit=False)
            # appareil.author = request.user
            # appareil.published_date = timezone.now()
            modalite.save()
            # return redirect('detail_modalite', modalite.id)
            return redirect('index')
    else:
        form = ModaliteForm(instance=modalite)
        # form =ModaliteForm()
    return render(request, 'imagerie/edit_modalite.html', {'form': form})
    print(request)