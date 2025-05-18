from django.test import TestCase
from django.urls import reverse
from cinephoria_webapp.models import Film, Seance, Genre, Salle, Cinema, Qualite
from django.utils import timezone
from datetime import date, time

class FilmsViewTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(genre="Drame")
        self.cinema = Cinema.objects.create(nom="Cinephoria Marseille", ville="Marseille")
        self.qualite = Qualite.objects.create(type_qualite="4K", prix_seance=10)
        self.salle = Salle.objects.create(
            numero_salle=5, total_places=120, places_pmr=8,
            qualite=self.qualite, cinema=self.cinema
        )
        self.film = Film.objects.create(titre="Mon Film Test", genre=self.genre, duree=100, affiche=None)

        self.seance = Seance.objects.create(
            film=self.film,
            salle=self.salle,
            heure_debut=time(18, 0),
            jours_diffusion=[date.today().weekday()]  # correspond au jour actuel
        )

    def test_films_view_filters(self):
        response = self.client.get(reverse("films"), {
            "cinema": self.cinema.id,
            "genre": self.genre.id,
            "jour": date.today().weekday()
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mon Film Test")
