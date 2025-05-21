from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import time
from cinephoria_webapp.models import Film, Seance, Reservation, Salle, Cinema, Qualite, Genre

class EspaceUtilisateurTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="TestPass123!", nom="Test", prenom="User"
        )
        self.client.login(email="user@test.com", password="TestPass123!")

    def test_acces_espace_utilisateur(self):
        response = self.client.get(reverse("mon_espace"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mes réservations")

    def test_acces_espace_non_connecte(self):
        self.client.logout()
        response = self.client.get(reverse("mon_espace"))
        self.assertEqual(response.status_code, 302)  # redirection login
        self.assertIn("/login", response.url)

    def test_soumission_avis_apres_reservation(self):
        # Setup minimal d'un film et séance passée
        genre = Genre.objects.create(genre="Test")
        heure = time(10, 0)
        qualite = Qualite.objects.create(type_qualite="Standard", prix_seance=10)
        cinema = Cinema.objects.create(nom="CinéTest")
        salle = Salle.objects.create(numero_salle="1", total_places=100, qualite=qualite, cinema=cinema)
        film = Film.objects.create(titre="Test Film", genre=genre, dernier_modificateur=self.user)
        seance = Seance.objects.create(film=film, salle=salle, heure_debut=heure, jours_diffusion=[0])

        Reservation.objects.create(utilisateur=self.user, seance=seance, nombre_places=2)

        response = self.client.get(reverse("noter_film", kwargs={"film_id": film.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre note")
