from django.contrib import admin
from django.urls import path, include, re_path
from imagerie import views

urlpatterns = [
    path('', views.index, name="index"),
    path('appareil', views.list_appareil, name='list_appareil'),
    path('machine', views.list_machine, name='list_machine'),
    path('etablissement', views.list_etablissement, name='list_etablissement'),
    path('localisation', views.list_localisation, name='list_localisation'),
    path('marque', views.list_marque, name='list_marque'),
    path('appareiltype', views.list_appareiltype, name='list_appareiltype'),
    path('modalite', views.list_modalite, name='list_modalite'),
    path('serveur', views.list_serveur, name='list_serveur'),
    path('vlan', views.list_vlan, name='list_vlan'),
    re_path(r'appareil/detail/(?P<appareil_id>\d+)', views.detail_appareil, name='detail_appareil'),
    re_path(r'machine/detail/(?P<machine_id>\d+)', views.detail_machine, name='detail_machine'),
    re_path(r'etablissement/detail/(?P<etablissement_id>\d+)', views.detail_etablissement, name='detail_etablissement'),
    re_path(r'localisation/detail/(?P<localisation_id>\d+)', views.detail_localisation, name='detail_localisation'),
    re_path(r'marque/detail/(?P<marque_id>\d+)', views.detail_marque, name='detail_marque'),
    re_path(r'appareiltype/detail/(?P<appareiltype_id>\d+)', views.detail_appareiltype, name='detail_appareiltype'),
    re_path(r'modalite/detail/(?P<modalite_id>\d+)', views.detail_modalite, name='detail_modalite'),
    re_path(r'serveur/detail/(?P<serveur_id>\d+)', views.detail_serveur, name='detail_serveur'),
    re_path(r'vlan/detail/(?P<vlan_id>\d+)', views.detail_vlan, name='detail_vlan'),
]
