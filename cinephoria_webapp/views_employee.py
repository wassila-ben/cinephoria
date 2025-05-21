from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Film, Seance, Salle, Incident, Avis
from django import forms
from .forms_admin import FilmForm, SeanceForm, SalleForm
from .decorators import employee_required

# Décorateur spécifique aux employés
def employee_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à votre espace employé.")
            return redirect('login')
        if not request.user.is_staff or request.user.is_superuser:
            messages.error(request, "Accès réservé aux employés.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Tableau de bord
@login_required
@employee_required
def employee_dashboard(request):
    nb_films = Film.objects.count()
    return render(request, 'cinephoria_webapp/employee_panel/dashboard.html', {
        'nb_films': nb_films,
    })

# Liste des films
@login_required
@employee_required
def employee_film_list(request):
    films = Film.objects.all()
    return render(request, 'cinephoria_webapp/employee_panel/film_list.html', {'films': films})

# Création
@login_required
@employee_required
def employee_film_create(request):
    if request.method == 'POST':
        form = FilmForm(request.POST, request.FILES)
        if form.is_valid():
            film = form.save(commit=False)
            film.dernier_modificateur = request.user
            film.save()
            form.save_m2m()
            messages.success(request, "Film ajouté avec succès.")
            return redirect('employee_film_list')
    else:
        form = FilmForm()
    return render(request, 'cinephoria_webapp/employee_panel/film_form.html', {'form': form})

# Modification
@login_required
@employee_required
def employee_film_update(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if request.method == 'POST':
        form = FilmForm(request.POST, request.FILES, instance=film)
        if form.is_valid():
            film = form.save(commit=False)
            film.dernier_modificateur = request.user
            film.save()
            form.save_m2m()
            messages.success(request, "Film modifié avec succès.")
            return redirect('employee_film_list')
    else:
        form = FilmForm(instance=film)
    return render(request, 'cinephoria_webapp/employee_panel/film_form.html', {'form': form})

# Suppression
@login_required
@employee_required
def employee_film_delete(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if request.method == 'POST':
        film.delete()
        messages.success(request, "Film supprimé.")
    return redirect('employee_film_list')

# Liste des séances
@login_required
@employee_required
def employee_seance_list(request):
    seances = Seance.objects.select_related('film', 'salle').all()
    return render(request, 'cinephoria_webapp/employee_panel/seance_list.html', {'seances': seances})

# Création
@login_required
@employee_required
def employee_seance_create(request):
    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance ajoutée.")
            return redirect('employee_seance_list')
    else:
        form = SeanceForm()
    return render(request, 'cinephoria_webapp/employee_panel/seance_form.html', {'form': form})

# Modification
@login_required
@employee_required
def employee_seance_update(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    if request.method == 'POST':
        form = SeanceForm(request.POST, instance=seance)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance modifiée.")
            return redirect('employee_seance_list')
    else:
        form = SeanceForm(instance=seance)
    return render(request, 'cinephoria_webapp/employee_panel/seance_form.html', {'form': form})

# Suppression
@login_required
@employee_required
def employee_seance_delete(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    if request.method == 'POST':
        seance.delete()
        messages.success(request, "Séance supprimée.")
    return redirect('employee_seance_list')

# Liste des salles
@login_required
@employee_required
def employee_salle_list(request):
    salles = Salle.objects.select_related('cinema', 'qualite').all()
    return render(request, 'cinephoria_webapp/employee_panel/salle_list.html', {'salles': salles})

# Création
@login_required
@employee_required
def employee_salle_create(request):
    form = SalleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Salle créée avec succès.")
        return redirect('employee_salle_list')
    return render(request, 'cinephoria_webapp/employee_panel/salle_form.html', {'form': form})

# Modification
@login_required
@employee_required
def employee_salle_update(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)
    form = SalleForm(request.POST or None, instance=salle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Salle modifiée.")
        return redirect('employee_salle_list')
    return render(request, 'cinephoria_webapp/employee_panel/salle_form.html', {'form': form})

# Suppression
@login_required
@employee_required
def employee_salle_delete(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)
    if request.method == 'POST':
        salle.delete()
        messages.success(request, "Salle supprimée.")
    return redirect('employee_salle_list')

from .models import Avis
from django.contrib.auth.decorators import login_required
from .decorators import employee_required

@login_required
@employee_required
def employee_review_list(request):
    avis = Avis.objects.select_related('utilisateur', 'film').order_by('-date')
    return render(request, 'cinephoria_webapp/employee_panel/avis_list.html', {'avis': avis})

@login_required
@employee_required
def employee_review_validate(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    avis.valide = True
    avis.save()
    messages.success(request, "Avis validé.")
    return redirect('employee_review_list')

@login_required
@employee_required
def employee_review_delete(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    avis.delete()
    messages.success(request, "Avis supprimé.")
    return redirect('employee_review_list')

@login_required
@employee_required
def employee_dashboard(request):
    stats = {
        'nb_films': Film.objects.count(),
        'nb_seances': Seance.objects.count(),
        'nb_salles': Salle.objects.count(),
        'avis_en_attente': Avis.objects.filter(valide=False).count()
    }
    return render(request, 'cinephoria_webapp/employee_panel/dashboard.html', {'stats': stats})
