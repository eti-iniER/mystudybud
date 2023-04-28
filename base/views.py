from django.shortcuts import render
from django.http import HttpResponse
from .models import Room

# Create your views here.

rooms = [
    {'id': 1,
     'name': "Let's learn Python!"},
     {'id': 2,
     'name': "Design with me"},
     {'id': 3,
     'name': "Front end developers"},
]

def index(request):
    rooms = Room.objects.all()
    contex = {'rooms': rooms}
    return render(request, 'base/index.html', contex)

def room(request, pk):
    this_room = Room.objects.get(id=pk)
    
    context = {'room': this_room}

    return render(request, 'base/room.html', context)