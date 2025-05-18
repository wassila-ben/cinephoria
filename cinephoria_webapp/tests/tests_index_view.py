from django.test import TestCase
from django.urls import reverse
from cinephoria_webapp.models import Cinema, Genre, Film, Salle, Seance, Qualite
from django.utils import timezone
from datetime import time, timedelta

class IndexCinemaFilterTest(TestCase):
    def setUp(self):
        genre = Genre.objects.create(genre="Action")
        qualite = Qualite.objects.create(type_qualite="2D", prix_seance=8)

        self.cinema1 = Cinema.objects.create(nom="Cinephoria Paris", ville="Paris")
        self.cinema2 = Cinema.objects.create(nom="Cinephoria Nantes", ville="Nantes")

        salle1 = Salle.objects.create(numero_salle=1, total_places=80, places_pmr=4, qualite=qualite, cinema=self.cinema1)
        salle2 = Salle.objects.create(numero_salle=2, total_places=100, places_pmr=6, qualite=qualite, cinema=self.cinema2)

        self.film_paris = Film.objects.create(titre="Film Paris", genre=genre, duree=120)
        self.film_nantes = Film.objects.create(titre="Film Nantes", genre=genre, duree=110)

        # Calcule du dernier mercredi pour le date_ajout
        today = timezone.now().date()
        days_since_wednesday = (today.weekday() - 2) % 7
        last_wednesday = today - timedelta(days=days_since_wednesday)

        # Ajout du champ date_ajout à chaque film
        self.film_paris.date_ajout = last_wednesday
        self.film_paris.save()

        self.film_nantes.date_ajout = last_wednesday
        self.film_nantes.save()

        Seance.objects.create(film=self.film_paris, salle=salle1, heure_debut=time(15, 0), jours_diffusion=[2])
        Seance.objects.create(film=self.film_nantes, salle=salle2, heure_debut=time(18, 0), jours_diffusion=[3])

    def test_films_filtered_by_cinema_paris(self):
        response = self.client.get(reverse("index"), {"cinema": self.cinema1.id})
        self.assertContains(response, "Film Paris")
        self.assertNotContains(response, "Film Nantes")

    def test_films_filtered_by_cinema_nantes(self):
        response = self.client.get(reverse("index"), {"cinema": self.cinema2.id})
        self.assertContains(response, "Film Nantes")
        self.assertNotContains(response, "Film Paris")
