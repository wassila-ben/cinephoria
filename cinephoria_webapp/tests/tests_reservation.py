from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cinephoria_webapp.models import (
    Genre, Qualite, Cinema, Salle, Film, Seance, Reservation, ReservationSiege, Siege
)
from datetime import time
from django.utils import timezone

class ReservationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password123"
        )

        self.genre = Genre.objects.create(genre="Action")
        self.qualite = Qualite.objects.create(type_qualite="4DX", prix_seance=10.5)
        self.cinema = Cinema.objects.create(nom="Cinéma Test", ville="Testville")
        self.salle = Salle.objects.create(cinema=self.cinema, qualite=self.qualite, total_places=50)
        self.film = Film.objects.create(titre="Film Test", duree=100, genre=self.genre)
        self.seance = Seance.objects.create(
            film=self.film,
            salle=self.salle,
            heure_debut=time(18, 30),
            jours_diffusion=[timezone.now().weekday()]
        )
        self.siege1 = Siege.objects.create(salle=self.salle, rangee="A", numero_siege=1, place_pmr=False)
        self.siege2 = Siege.objects.create(salle=self.salle, rangee="A", numero_siege=2, place_pmr=False)

    def test_reservation_complete_flow(self):
        self.client.login(email="test@example.com", password="password123")

        # Étape 1 : Réservation (formulaire)
        response = self.client.post(reverse('reservation'), {
            "film": self.film.id,
            "cinema": self.cinema.id,
            "jour": timezone.now().date().isoformat(),
            "heure": "18:30",
            "nombre_places": 2,
            "places_pmr": False,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('choix_sieges'))

        # Étape 2 : Choix des sièges
        session = self.client.session
        data = session.get("reservation_data")
        self.assertIsNotNone(data)

        response = self.client.post(reverse('choix_sieges'), {
            "sieges": [self.siege1.id, self.siege2.id]
        }, follow=True)

        self.assertRedirects(response, reverse("reservation_confirmation"))

        # Vérifier que la réservation est bien créée
        reservation = Reservation.objects.filter(utilisateur=self.user).first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.nombre_places, 2)

        # Vérifie les billets
        self.assertEqual(reservation.billet_set.count(), 2)
