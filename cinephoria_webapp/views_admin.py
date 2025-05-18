from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms_admin import FilmForm, SeanceForm, SalleForm, EmployeCreationForm
from .models import Film, Seance, Salle, Utilisateur
from django.shortcuts import redirect, get_object_or_404
from cinephoria_webapp.mongo_utils import get_reservations_last_7_days

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect('login')  
        if not request.user.is_superuser:
            messages.error(request, "Accès refusé : vous n'avez pas les droits d'administration.")
            return redirect('index')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@superuser_required
@login_required
def admin_dashboard(request):
    nb_films = Film.objects.count()
    nb_seances = Seance.objects.count()
    nb_salles = Salle.objects.count()

    mongo_data = get_reservations_last_7_days()
    nb_reservations = sum([item['total'] for item in mongo_data])

    context = {
        'nb_films': nb_films,
        'nb_seances': nb_seances,
        'nb_salles': nb_salles,
        'nb_reservations': nb_reservations,
    }

    return render(request, 'cinephoria_webapp/admin_panel/admin_dashboard.html', context)


@login_required
@superuser_required
def film_list(request):
    films = Film.objects.all()
    return render(request, 'cinephoria_webapp/admin_panel/film_list.html', {'films': films})

@login_required
@superuser_required
def film_create(request):
    if request.method == 'POST':
        form = FilmForm(request.POST, request.FILES)
        if form.is_valid():
            film = form.save(commit=False)
            film.dernier_modificateur = request.user
            film.save()
            form.save_m2m()
            messages.success(request, "Film ajouté avec succès.")
            return redirect('admin_film_list')
    else:
        form = FilmForm()
    return render(request, 'cinephoria_webapp/admin_panel/film_form.html', {'form': form})

@login_required
@superuser_required
def film_update(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    if request.method == 'POST':
        form = FilmForm(request.POST, request.FILES, instance=film)
        if form.is_valid():
            film = form.save(commit=False)
            film.dernier_modificateur = request.user
            film.save()
            form.save_m2m()
            messages.success(request, "Film modifié avec succès.")
            return redirect('admin_film_list')
    else:
        form = FilmForm(instance=film)
    return render(request, 'cinephoria_webapp/admin_panel/film_form.html', {'form': form})

@login_required
@superuser_required
def film_delete(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    film.delete()
    messages.success(request, "Film supprimé.")
    return redirect('admin_film_list')

@superuser_required
@login_required
def seance_list(request):
    seances = Seance.objects.select_related('film', 'salle').all()
    return render(request, 'cinephoria_webapp/admin_panel/seance_list.html', {'seances': seances})

@superuser_required
@login_required
def seance_create(request):
    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance ajoutée.")
            return redirect('admin_seance_list')
    else:
        form = SeanceForm()
    return render(request, 'cinephoria_webapp/admin_panel/seance_form.html', {'form': form})

@superuser_required
@login_required
def seance_update(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    if request.method == 'POST':
        form = SeanceForm(request.POST, instance=seance)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance modifiée.")
            return redirect('admin_seance_list')
    else:
        form = SeanceForm(instance=seance)
    return render(request, 'cinephoria_webapp/admin_panel/seance_form.html', {'form': form})

@superuser_required
@login_required
def seance_delete(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    seance.delete()
    messages.success(request, "Séance supprimée.")
    return redirect('admin_seance_list')

@superuser_required
@login_required
def salle_list(request):
    salles = Salle.objects.select_related('cinema', 'qualite').all()
    return render(request, 'cinephoria_webapp/admin_panel/salle_list.html', {'salles': salles})

@superuser_required
@login_required
def salle_create(request):
    form = SalleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Salle créée avec succès.")
        return redirect('admin_salle_list')
    return render(request, 'cinephoria_webapp/admin_panel/salle_form.html', {'form': form})

@superuser_required
@login_required
def salle_update(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)
    form = SalleForm(request.POST or None, instance=salle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Salle modifiée.")
        return redirect('admin_salle_list')
    return render(request, 'cinephoria_webapp/admin_panel/salle_form.html', {'form': form})

@superuser_required
@login_required
def salle_delete(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)
    salle.delete()
    messages.success(request, "Salle supprimée.")
    return redirect('admin_salle_list')

@superuser_required
@login_required
def employe_create(request):
    if request.method == 'POST':
        form = EmployeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé créé avec succès.")
            return redirect('admin_dashboard')
    else:
        form = EmployeCreationForm()
    return render(request, 'cinephoria_webapp/admin_panel/employe_form.html', {'form': form})

from .forms_admin import ResetEmployePasswordForm

@superuser_required
@login_required
def employe_reset_password(request):
    if request.method == 'POST':
        form = ResetEmployePasswordForm(request.POST)
        if form.is_valid():
            employe = form.cleaned_data['employe']
            nouveau_mdp = form.cleaned_data['nouveau_mot_de_passe']
            employe.set_password(nouveau_mdp)
            employe.save()
            messages.success(request, f"Mot de passe réinitialisé pour {employe.email}.")
            return redirect('admin_dashboard')
    else:
        form = ResetEmployePasswordForm()
    return render(request, 'cinephoria_webapp/admin_panel/employe_reset.html', {'form': form})

@superuser_required
@login_required
def dashboard_reservations(request):
    raw_data = get_reservations_last_7_days()
    data = []

    for item in raw_data:
        film = item['_id']
        total = item['total']

        if total > 50:
            color = 'success'
        elif 20 <= total <= 50:
            color = 'warning'
        else:
            color = 'danger'

        data.append({
            'film': film,
            'total': total,
            'color': color,
        })

    return render(request, 'cinephoria_webapp/admin_panel/dashboard_reservations.html', {'data': data})
