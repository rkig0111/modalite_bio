from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse
from .models import Vlan

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def list_vlan(request):
    try:
        vlans = Vlan.objects.all()
    except Vlan.DoesNotExist:
        raise Http404("Vlan does not exist")
    print("vlans ---->  ", vlans)
    return render(request, "imagerie/list_vlan.html", {"vlans": vlans})