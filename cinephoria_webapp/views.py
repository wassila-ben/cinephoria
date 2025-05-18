from django.shortcuts import render, get_object_or_404, redirect
from .models import Film, Cinema, Avis, Seance, Reservation, Genre, Utilisateur, ReservationSiege
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ReservationForm, SiegeSelectionForm
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme





def base(request):
    cinema_id = request.GET.get('cinema_id')
    cinema = get_object_or_404(Cinema, id=cinema_id) if cinema_id else Cinema.objects.first()
    return render(request, 'cinephoria_webapp/base.html', {'cinema': cinema})


def index(request):
    user = request.user
    cinemas = Cinema.objects.all()

    # 1. Cinéma passé dans l'URL (manuellement sélectionné)
    
    cinema_id = request.GET.get("cinema")
    if cinema_id:
        selected_cinema = get_object_or_404(Cinema, id=cinema_id)
        request.session["cinema_id"] = cinema_id  # sauvegarde pour les prochaines fois
    else:
        # 2. Cinéma en session
        cinema_id = request.session.get("cinema_id")
        selected_cinema = Cinema.objects.filter(id=cinema_id).first()

        # 3. Si toujours rien, on prends la ville de l'utilisateur
        if not selected_cinema and user.is_authenticated:
            selected_cinema = Cinema.objects.filter(ville=user.ville).first()
    
    if cinema_id == "all":
        selected_cinema = None
        request.session.pop("cinema_id", None)


    # 4. Calcul du dernier mercredi
    today = timezone.now().date()
    days_since_wednesday = (today.weekday() - 2) % 7
    last_wednesday = today - timedelta(days=days_since_wednesday)

    # 5. Films selon sélection ou par défaut
    if selected_cinema is not None:
        films = Film.objects.filter(
            date_ajout=last_wednesday,
            seance__salle__cinema=selected_cinema).distinct()
        films_avenir = Film.objects.filter(
            date_ajout__gt=last_wednesday,
            seance__salle__cinema=selected_cinema).distinct()[:8]
    else:
        films = Film.objects.filter(
            date_ajout=last_wednesday,
            seance__isnull=False).distinct()
        films_avenir = Film.objects.filter(
            date_ajout__gt=last_wednesday,
            seance__isnull=False).distinct()[:8]
    
    now = timezone.now()
    today = now.date()
    current_weekday = today.weekday()  # 0 = lundi
    current_time = now.time()

    film_seances_dict = {}

    for film in films:
        seances = Seance.objects.filter(film=film).select_related('salle', 'salle__qualite')

        prochaines_seances = []
        for seance in seances:
            for jour in seance.jours_diffusion:
                jour = int(jour) # Convertir en entier
                days_until = (jour - current_weekday) % 7
                seance_date = today + timedelta(days=days_until)

                if days_until == 0 and seance.heure_debut <= current_time:
                    continue

                seance_datetime = datetime.combine(seance_date, seance.heure_debut)
                prochaines_seances.append((seance_datetime, seance))

        prochaines_seances.sort()
        film_seances_dict[film.id] = [{
            "seance": s[1],
            "date": s[0].date(),
            "cinema": s[1].salle.cinema.nom,
        } for s in prochaines_seances[:3]]


    context = {
        "cinemas": cinemas,
        "cinema": selected_cinema,
        "films": films,
        "films_avenir": films_avenir,
        "last_wednesday": last_wednesday,
        "film_seances_dict": film_seances_dict,
    }

    return render(request, "cinephoria_webapp/index.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Connexion réussie.")

            # Vérifie que l'URL est sûre
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'cinephoria_webapp/login.html', {'form': form, 'next': next_url})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès.")
            return redirect('index')
        else:
            messages.error(request, "Une erreur est survenue, veuillez vérifier les informations.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'cinephoria_webapp/register.html', {'form': form})

def details_film(request, film_id):
    # Récupére le film
    film = get_object_or_404(Film, id=film_id)
    
    # Récupére toutes les séances associées au film
    seances = Seance.objects.filter(film=film).select_related('salle', 'salle__qualite')
    avis = Avis.objects.filter(film=film).select_related('utilisateur').order_by('-date')

    moyenne_notes = avis.aggregate(Avg('note'))['note__avg']

    reservations = None

    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(
            utilisateur=request.user,
            seance__film=film
        )

    else: reservations = None

    context = {
        'film': film,
        'seances': seances,
        'avis':avis,
        'reservations': reservations,
        'moyennes_notes': moyenne_notes,
    }
    return render(request, 'cinephoria_webapp/details_film.html', context)

def films_view(request):
    films = Film.objects.all()

    cinema_id = request.GET.get('cinema')
    genre_id = request.GET.get('genre')
    jour = request.GET.get('jour')

    if cinema_id:
        films = films.filter(seance__salle__cinema__id=cinema_id).distinct()

    if genre_id:
        films = films.filter(genre__id=genre_id)

    if jour:
        try:
            jour_date = parse_date(jour)
            if jour_date:
                films = films.filter(seance__heure_debut__date=jour_date).distinct()
        except ValueError:
            pass  # Si le jour est invalide, on ignore le filtre

    return render(request, 'cinephoria_webapp/films.html', {
        'films': films,
        'cinemas': Cinema.objects.all(),
        'genres': Genre.objects.all(),
    })

def choisir_cinema(request):
    if request.method == 'POST':
        cinema_id = request.POST.get("cinema_id")
        if cinema_id == "all":
            request.session.pop("cinema_id", None)  # Supprime la sélection de cinéma
        else:
            request.session["cinema_id"] = cinema_id
    return redirect('index')


@login_required
def reservation(request):
    if request.method == 'POST':
        step = request.POST.get('step')
        
        if step == '1':
            # Création du formulaire de réservation
            form = ReservationForm(request.POST)
            if form.is_valid():
                reservation_data = {
                    'seance_id': form.cleaned_data['seance'].id,
                    'nombre_places': form.cleaned_data['nombre_places'],
                    }
                request.session['reservation_data'] = reservation_data
                return redirect('choix_sieges')
        else:
            form = ReservationForm()
        return render(request, 'cinephoria_webapp/reservation.html', {'form': form})

    else:
        form = ReservationForm()
        return render(request, 'cinephoria_webapp/reservation.html', {'form': form})

@login_required
def choix_sieges(request):
    reservation_data = request.session.get('reservation_data')
    if not reservation_data:
        return redirect('reservation')

    seance_id = reservation_data['seance_id']
    seance = get_object_or_404(Seance, id=seance_id)
    nombre_places = reservation_data['nombre_places']

    if request.method == 'POST':
        form = SiegeSelectionForm(request.POST, seance=seance)
        if form.is_valid():
            sieges = form.cleaned_data['sieges']

            if len(sieges) != nombre_places:
                form.add_error('sieges', f"Vous devez sélectionner exactement {nombre_places} sièges.")
            else:
                # Vérifie si les sièges sont déjà réservés pour cette séance
                sieges_deja_reserves = ReservationSiege.objects.filter(
                    reservation__seance=seance,
                    siege__in=sieges
                ).exists()

                if sieges_deja_reserves:
                    form.add_error('sieges', "Un ou plusieurs sièges sélectionnés sont déjà réservés. Veuillez en choisir d'autres.")
                else:
                    # Création de la réservation
                    reservation = Reservation.objects.create(
                        utilisateur=request.user.utilisateur,
                        seance=seance,
                        nombre_places=nombre_places,
                    )
                    # Calcul du prix
                    reservation.calculer_prix()

                    # Lier les sièges à la réservation
                    for siege in sieges:
                        ReservationSiege.objects.create(
                            reservation=reservation,
                            siege=siege
                        )

                    return redirect('reservation_confirmation')
    else:
        form = SiegeSelectionForm(seance=seance)

    return render(request, 'cinephoria_webapp/choix_sieges.html', {
        'form': form,
        'nombre_places': nombre_places
    })

@login_required
def reservation_confirmation(request):
    return render(request, 'cinephoria_webapp/reservation_confirmation.html')
