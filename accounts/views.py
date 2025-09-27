from django.shortcuts import render


def home_view(request):
    return render(request, "home.html")

def arenas_view(request):
    return render(request, "arenas.html")

def contestants_view(request):
    return render(request, "contestants.html")

def howitworks_view(request):
    return render(request, "how-it-works.html")

def finaleroyale_view(request):
    return render(request, "finale-royale.html")
