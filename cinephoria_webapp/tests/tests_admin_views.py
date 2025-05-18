from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cinephoria_webapp.models import Film, Genre

class AdminViewAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.genre = Genre.objects.create(genre="Test Genre")

        self.admin = self.User.objects.create_superuser(
            email="admin@test.com",
            password="admin123",
            nom="Admin", prenom="Admin"
        )

        self.employe = self.User.objects.create_user(
            email="employe@test.com",
            password="123456",
            is_staff=True  # mais pas superuser
        )

    def test_employe_cannot_access_admin_dashboard(self):
        self.client.login(email="employe@test.com", password="123456")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # redirection

    def test_admin_can_delete_film(self):
        self.client.login(email="admin@test.com", password="admin123")
        film = Film.objects.create(titre="À Supprimer", duree=100, genre=self.genre)
        response = self.client.get(reverse('admin_film_delete', args=[film.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Film.objects.filter(id=film.id).exists())
