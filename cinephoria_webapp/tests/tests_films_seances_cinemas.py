from django.test import TestCase
from django.utils import timezone
from datetime import time
from cinephoria_webapp.models import Film, Seance, Salle, Cinema, Genre, Qualite

class FilmsSeancesCinemasModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(genre="Comédie")
        self.qualite = Qualite.objects.create(type_qualite="IMAX", prix_seance=12.50)
        self.cinema = Cinema.objects.create(nom="Cinephoria Lyon", ville="Lyon")
        self.salle = Salle.objects.create(
            numero_salle=1,
            total_places=100,
            places_pmr=5,
            qualite=self.qualite,
            cinema=self.cinema
        )
        self.film = Film.objects.create(
            titre="Le Grand Test",
            genre=self.genre,
            duree=90
        )
        self.seance = Seance.objects.create(
            film=self.film,
            salle=self.salle,
            heure_debut=time(14, 30),
            jours_diffusion=[2, 4]  # mercredi et vendredi
        )

    def test_film_creation(self):
        self.assertEqual(self.film.titre, "Le Grand Test")
        self.assertEqual(self.film.duree, 90)

    def test_seance_related_to_film_and_cinema(self):
        self.assertEqual(self.seance.film, self.film)
        self.assertEqual(self.seance.salle.cinema, self.cinema)
