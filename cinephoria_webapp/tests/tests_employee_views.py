from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time
from cinephoria_webapp.models import (
    Utilisateur, Genre, Film, Cinema, Qualite, Salle,
    Seance, Avis
)

class EmployeeViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.genre = Genre.objects.create(genre="Science-fiction")

        self.employe = Utilisateur.objects.create_user(
            email="employe@test.com",
            password="123456",
            nom="Jean",
            prenom="Dupont",
            is_staff=True
        )

        self.cinema = Cinema.objects.create(
            nom="Cinéma Lumière",
            adresse="123 rue du Test",
            cp="75000",
            ville="Paris",
            pays="France",
            telephone="0101010101"
        )

        self.qualite = Qualite.objects.create(
            type_qualite="4K",
            prix_seance=12.5
        )

        self.salle = Salle.objects.create(
            numero_salle="1",
            total_places=100,
            places_pmr=5,
            qualite=self.qualite,
            cinema=self.cinema
        )

        self.film = Film.objects.create(
            titre="Test Film",
            duree=120,
            genre=self.genre,
            dernier_modificateur=self.employe
        )
        self.film.cinemas.set([self.cinema])

        self.seance = Seance.objects.create(
            film=self.film,
            salle=self.salle,
            heure_debut=time(18, 0),
            jours_diffusion=[0, 2, 4]  # Lundi, Mercredi, Vendredi
        )

        self.avis = Avis.objects.create(
            utilisateur=self.employe,
            film=self.film,
            note=4.0,
            commentaire="Très bon film"
        )

        self.client.login(email="employe@test.com", password="123456")

    def test_access_dashboard(self):
        response = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_list_films(self):
        response = self.client.get(reverse('employee_film_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.film.titre)

    def test_create_film(self):
        data = {
            'titre': 'Nouveau Film',
            'duree': 110,
            'synopsis': 'Un super synopsis',
            'genre': self.genre.id,
            'age_minimum': 10,
            'note': 3.5,
            'cinemas': [self.cinema.id],
            'date_sortie': '2024-01-01',
            'date_ajout': '2024-01-01',
        }
        response = self.client.post(reverse('employee_film_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Film.objects.filter(titre='Nouveau Film').exists())

    def test_update_film(self):
        data = {
            'titre': 'Film Modifié',
            'duree': self.film.duree,
            'synopsis': self.film.synopsis,
            'genre': self.genre.id,
            'age_minimum': self.film.age_minimum,
            'note': self.film.note,
            'cinemas': [self.cinema.id],
            'date_sortie': '2024-01-01',
            'date_ajout': '2024-01-01',
        }
        response = self.client.post(reverse('employee_film_update', args=[self.film.id]), data)
        self.assertEqual(response.status_code, 302)
        self.film.refresh_from_db()
        self.assertEqual(self.film.titre, 'Film Modifié')


    def test_delete_film(self):
        response = self.client.post(reverse('employee_film_delete', args=[self.film.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Film.objects.filter(id=self.film.id).exists())

    def test_list_seances(self):
        response = self.client.get(reverse('employee_seance_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.film.titre)

    def test_review_validation(self):
        response = self.client.get(reverse('employee_review_validate', args=[self.avis.id]))
        self.assertEqual(response.status_code, 302)
        self.avis.refresh_from_db()
        self.assertTrue(self.avis.valide)

    def test_review_delete(self):
        response = self.client.get(reverse('employee_review_delete', args=[self.avis.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Avis.objects.filter(id=self.avis.id).exists())
