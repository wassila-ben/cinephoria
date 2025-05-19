from django.test import TestCase
from datetime import time
from django.urls import reverse
from django.contrib.auth import get_user_model
from cinephoria_webapp.models import Film, Salle, Seance, Cinema, Genre, Qualite

class ReservationTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com', password='password'
        )
        genre = Genre.objects.create(genre="Action")
        qualite = Qualite.objects.create(type_qualite="IMAX", prix_seance=12)
        cinema = Cinema.objects.create(nom="Test Cinéma")
        salle = Salle.objects.create(cinema=cinema, qualite=qualite, total_places=100)
        film = Film.objects.create(titre="Test Film", duree=90, genre=genre)
        self.seance = Seance.objects.create(
            film=film, salle=salle, heure_debut=time(18, 0), jours_diffusion=[0]
        )

    def test_reservation_requires_login(self):
        response = self.client.get(reverse('reservation'))
        self.assertRedirects(response, '/login/?next=/reservation/')

    def test_reservation_authenticated(self):
        self.client.login(email='testuser@example.com', password='password')
        response = self.client.get(reverse('reservation'))
        self.assertEqual(response.status_code, 200)
