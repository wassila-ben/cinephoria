from django.shortcuts import render, get_object_or_404, redirect
from .models import Film, Cinema, Avis, Seance, Reservation, Genre, Utilisateur, ReservationSiege, Siege, Billet
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ReservationForm, SiegeSelectionForm, ChoixSeanceForm, AvisForm, ContactForm
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.crypto import get_random_string






def base(request):
    cinema_id = request.GET.get('cinema_id')
    cinema = get_object_or_404(Cinema, id=cinema_id) if cinema_id else Cinema.objects.first()
    return render(request, 'cinephoria_webapp/base.html', {'cinema': cinema})


def index(request):
    user = request.user
    cinemas = Cinema.objects.all()

    cinema_id = request.GET.get("cinema")

    # 1. Si l'utilisateur a choisi "Tous les cinémas"
    if cinema_id == "all":
        selected_cinema = None
        request.session.pop("cinema_id", None)

    # 2. Si l'utilisateur a sélectionné un cinéma spécifique
    elif cinema_id:
        selected_cinema = get_object_or_404(Cinema, id=cinema_id)
        request.session["cinema_id"] = cinema_id

    # 3. Sinon, sur la session
    else:
        cinema_id = request.session.get("cinema_id")
        selected_cinema = Cinema.objects.filter(id=cinema_id).first()

    

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

        prochaines_seances.sort(key=lambda x: x[0])
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
    avis = Avis.objects.filter(film=film, valide=True).select_related('utilisateur').order_by('-date')

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
    jour = request.GET.get('jour')  # format attendu : "YYYY-MM-DD"

    if cinema_id:
        films = films.filter(seance__salle__cinema__id=cinema_id).distinct()

    if genre_id:
        films = films.filter(genre__id=genre_id)

    if jour:
        try:
            jour_date = parse_date(jour)
            if jour_date:
                jour_index = jour_date.weekday()  # 0 = Lundi, ..., 6 = Dimanche
                films = films.filter(seance__jours_diffusion__contains=[jour_index]).distinct()
        except ValueError:
            pass

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
    return redirect(request.META.get('HTTP_REFERER', 'index'))



@login_required
def reservation(request):
    seance_id = request.GET.get('seance_id')
    selected_seance = None
    film = None
    seance = None

    if seance_id:
        try:
            selected_seance = Seance.objects.select_related('film', 'salle', 'salle__cinema').get(id=seance_id)
            film = selected_seance.film
        except Seance.DoesNotExist:
            messages.warning(request, "Séance introuvable.")
            return redirect('films_view')

    # Pré-sélections par défaut
    selected_film_id = request.POST.get("film") if request.method == "POST" else None
    selected_jour = request.POST.get("jour") if request.method == "POST" else None
    selected_heure = request.POST.get("heure") if request.method == "POST" else None
    selected_cinema = request.POST.get("cinema") if request.method == "POST" else None

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            if not (selected_film_id and selected_jour and selected_heure):
                messages.error(request, "Veuillez remplir tous les champs requis.")
            else:
                try:
                    film = Film.objects.get(id=selected_film_id)
                    heure_obj = datetime.strptime(selected_heure, "%H:%M").time()
                    jour_obj = datetime.strptime(selected_jour, "%Y-%m-%d").date()

                    seance = Seance.objects.filter(
                        film=film,
                        heure_debut=heure_obj,
                        jours_diffusion__contains=[jour_obj.weekday()]
                    ).first()

                    if not seance:
                        messages.error(request, "Aucune séance ne correspond à votre sélection.")
                    else:
                        request.session['reservation_data'] = {
                            'seance_id': seance.id,
                            'nombre_places': form.cleaned_data['nombre_places'],
                            'places_pmr': form.cleaned_data.get('places_pmr', False),
                        }
                        return redirect('choix_sieges')

                except (Film.DoesNotExist, ValueError):
                    messages.error(request, "Sélection invalide.")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ReservationForm(initial={'seance': selected_seance})

    return render(request, 'cinephoria_webapp/reservation.html', {
        'form': form,
        'film': film,
        'seance': seance or selected_seance,
        'films': Film.objects.all(),
        'selected_film_id': selected_film_id,
        'selected_jour': selected_jour,
        'selected_heure': selected_heure,
        'selected_cinema': selected_cinema,
    })


@login_required
def choix_sieges(request):
    data = request.session.get('reservation_data')
    if not data:
        return redirect('reservation')

    seance = get_object_or_404(Seance, id=data['seance_id'])
    nombre_places = data['nombre_places']
    places_pmr = data.get('places_pmr', False)

    sieges = seance.salle.sieges.all().order_by('rangee', 'numero_siege')
    sieges_disponibles = [s for s in sieges if not ReservationSiege.objects.filter(reservation__seance=seance, siege=s).exists()]

    if request.method == 'POST':
        selected_ids = request.POST.getlist('sieges')
        if len(selected_ids) != nombre_places:
            messages.error(request, f"Veuillez sélectionner exactement {nombre_places} sièges.")
        else:
            selected = Siege.objects.filter(id__in=selected_ids)
            if places_pmr and not any(s.place_pmr for s in selected):
                messages.error(request, "Vous avez demandé des places PMR mais n’en avez pas sélectionné.")
            elif not places_pmr and any(s.place_pmr for s in selected):
                messages.error(request, "Vous avez sélectionné un siège PMR sans l’avoir demandé.")
            else:
                reservation = Reservation.objects.create(
                    utilisateur=request.user,
                    seance=seance,
                    nombre_places=nombre_places
                )
                for siege in selected:
                    ReservationSiege.objects.create(reservation=reservation, siege=siege)

                # Créer un seul billet après
                if not hasattr(reservation, 'billet'):
                    Billet.objects.create(reservation=reservation)

                # Calculer le prix total
                reservation.calculer_prix()
                return redirect('reservation_confirmation')

    # Regroupe les sièges par rangée
    sieges_by_rangee = {}
    for s in sieges:
        sieges_by_rangee.setdefault(s.rangee, []).append({
            'id': s.id,
            'numero': s.numero_siege,
            'reserve': ReservationSiege.objects.filter(reservation__seance=seance, siege=s).exists(),
            'pmr': s.place_pmr,
        })

        print("sieges_by_rangee=", sieges_by_rangee)
    
    prix_unitaires = seance.salle.qualite.prix_seance
    prix_total = prix_unitaires * nombre_places

    return render(request, 'cinephoria_webapp/choix_sieges.html', {
        'sieges_by_rangee': sieges_by_rangee,
        'seance': seance,
        'nombre_places': nombre_places,
        'places_pmr': places_pmr,
        'prix_unitaires': prix_unitaires,
        'prix_total': prix_total,
    })

@login_required
def reservation_confirmation(request):
    reservation = Reservation.objects.filter(utilisateur=request.user).order_by('-id').first()

    if not reservation:
        messages.error(request, "Aucune réservation trouvée.")
        return redirect('index')

    # cherche la date réelle de la séance
    seance = reservation.seance
    now = timezone.now()
    today = now.date()
    current_weekday = today.weekday()

    # cherche le prochain jour correspondant à la séance
    jour_reel = None
    for i in range(7):
        candidate = today + timedelta(days=i)
        if candidate.weekday() in seance.jours_diffusion:
            jour_reel = candidate
            break

    billets = [reservation.billet] if hasattr(reservation, 'billet') else []
    context = {
        "reservation": reservation,
        "billets": billets,
        "jour_reel": jour_reel,
        "heure": seance.heure_debut,
    }

    return render(request, 'cinephoria_webapp/reservation_confirmation.html', context)

@login_required
def mon_espace(request):
    reservations = Reservation.objects.filter(utilisateur=request.user).select_related(
        'seance__film', 'seance__salle__cinema'
    ).order_by('-date_reservation')

    now = timezone.now()

    for res in reservations:
        # Combine le jour + heure de la séance (si ton modèle a un champ `jour`)
        try:
            res.date_complete = datetime.combine(res.jour, res.seance.heure_debut)
        except AttributeError:
            res.date_complete = None  # pour éviter plantage

        # Si tu as un champ de QR code (ex : fichier ou URL)
        try:
            billet =res.billet
            res.qr_code_url = billet.qr_code.url if billet.qr_code else None
        except Billet.DoesNotExist:
            res.qr_code_url = None

    return render(request, 'cinephoria_webapp/mon_espace.html', {
        'reservations': reservations,
        'now': now
    })

@login_required
def noter_film(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    existing_avis = Avis.objects.filter(film=film, utilisateur=request.user).first()

    if existing_avis:
        messages.warning(request, "Vous avez déjà noté ce film.")
        return redirect('mon_espace')

    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.film = film
            avis.utilisateur = request.user
            avis.valide = False
            avis.save()
            messages.success(request, "Votre avis a été soumis pour validation.")
            return redirect('mon_espace')
    else:
        form = AvisForm()

    return render(request, 'cinephoria_webapp/noter_film.html', {'film': film, 'form': form})

# def reset_password(request):
    if request.method == 'POST':
        form = MotDePasseOublieForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                utilisateur = Utilisateur.objects.get(email=email)
                nouveau_mdp = get_random_string(length=10)
                utilisateur.set_password(nouveau_mdp)
                utilisateur.doit_changer_mdp = True
                utilisateur.save()

                send_mail(
                    "Réinitialisation de votre mot de passe",
                    f"Bonjour,\n\nVoici votre nouveau mot de passe temporaire : {nouveau_mdp}\n\nMerci de le changer dès votre prochaine connexion.",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Un mot de passe temporaire vous a été envoyé par email.")
                return redirect('login')
            except Utilisateur.DoesNotExist:
                messages.warning(request, "Aucun compte ne correspond à cet email.")
    else:
        form = MotDePasseOublieForm()

    return render(request, 'cinephoria_webapp/reset_password.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if request.user.is_authenticated:
                contact.utilisateur = request.user
            else:
                messages.error(request, "Vous devez être connecté pour envoyer une demande.")
                return redirect('login')
            contact.save()

            # Envoi d'un mail générique
            send_mail(
                subject=f"[Contact] {contact.objet_demande}",
                message=f"{contact.nom or 'Anonyme'}\nCinéma : {contact.cinema}\n\n{contact.description}",
                from_email=None,
                recipient_list=['support@cinephoria.com'],
                fail_silently=True
            )

            messages.success(request, "Votre demande a été envoyée.")
            return redirect('index')
    else:
        form = ContactForm()
    
    return render(request, 'cinephoria_webapp/contact.html', {'form': form})
