from django.contrib import admin
from django.urls import path, include, re_path
from imagerie import views

urlpatterns = [
    path('', views.index, name="index"),
    path('machine/', views.list_machine, name='list_machine'),
    path('appareil/', views.list_appareil, name='list_appareil'),
    path('modalite/', views.list_modalite, name='list_modalite'),
    path('etablissement', views.list_etablissement, name='list_etablissement'),
    path('localisation', views.list_localisation, name='list_localisation'),
    path('marque', views.list_marque, name='list_marque'),
    path('appareiltype', views.list_appareiltype, name='list_appareiltype'),
    path('modalite', views.list_modalite, name='list_modalite'),
    path('serveur', views.list_serveur, name='list_serveur'),
    path('vlan', views.list_vlan, name='list_vlan'),
    #
    path('appareil/<int:id>/', views.detail_appareil, name='detail_appareil'),
    path('machine/<int:id>/', views.detail_machine, name='detail_machine'),
    path('modalite/<int:id>/', views.detail_modalite, name='detail_modalite'),
    path('edit_appareil/<int:id>/', views.edit_appareil, name='edit_appareil'),
    path('edit_modalite/<int:id>/', views.edit_modalite, name='edit_modalite'),
]
