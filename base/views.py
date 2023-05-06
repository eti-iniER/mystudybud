from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.

rooms = [
    {"id": 1, "name": "Let's learn Python!"},
    {"id": 2, "name": "Design with me"},
    {"id": 3, "name": "Front end developers"},
]


def login_page(request):
    page = "login_page"
    if request.user.is_authenticated:
        return redirect(reverse("index"))

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist!")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse("index"))
        else:
            messages.error(request, "Username/password does not exist!")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)
    return redirect("index")


def register_page(request):
    #
    form = UserCreationForm

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect(reverse("index"))
        else:
            messages.error(request, "An error occured during registration")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


def index(request):
    query = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=query)
        | Q(name__icontains=query)
        | Q(description__icontains=query)
    )

    room_count = rooms.count()
    topics = Topic.objects.all()

    context = {"rooms": rooms, "topics": topics, "count": room_count}
    return render(request, "base/index.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    participants = room.participants.all()
    room_messages = room.message_set.all()

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("rooms", pk=room.id)

    return render(request, "base/room.html", context)


@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("index")

    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You can't delete this!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)

        if form.is_valid():
            form.save()
            return redirect("index")

    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="/login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You can't delete this!")

    if request.method == "POST":
        room.delete()
        return redirect("index")

    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="/login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You can't delete this!")

    if request.method == "POST":
        message.delete()
        return redirect("index")

    return render(request, "base/delete.html", {"obj": message})
