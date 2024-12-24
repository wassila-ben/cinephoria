from django.shortcuts import render

# Create your views here.

 
def base(request):
    return render(request, 'cinephoria_webapp/base.html')

def index(request):
    return render(request, 'cinephoria_webapp/index.html')

def details(request):
    return render(request, 'cinephoria_webapp/details.html')

def films(request):
    return render(request, 'cinephoria_webapp/films.html')

def reservation(request):
    return render(request, 'cinephoria_webapp/reservation.html')

def contact(request):
    return render(request, 'cinephoria_webapp/contact.html')

def login(request):
    return render(request, 'cinephoria_webapp/login.html')