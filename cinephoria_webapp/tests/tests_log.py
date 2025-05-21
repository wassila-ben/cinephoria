from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

class AuthentificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="login@test.com", password="Login123!", nom="Login", prenom="User"
        )

    def test_connexion_valide(self):
        response = self.client.post(reverse("login"), {
            "username": "login@test.com",
            "password": "Login123!"
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion

    def test_connexion_invalide(self):
        response = self.client.post(reverse("login"), {
            "username": "login@test.com",
            "password": "MauvaisMotDePasse"
        })
        self.assertContains(response, "Email ou mot de passe incorrect.")

    def test_vue_password_reset_get(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "email")

    def test_password_reset_envoie_email(self):
        response = self.client.post(reverse("password_reset"), {
            "email": "login@test.com"
        })
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Réinitialisation", mail.outbox[0].subject)
