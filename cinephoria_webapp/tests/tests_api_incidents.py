from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from cinephoria_webapp.models import Utilisateur, Salle, Incident, Siege, Cinema, Qualite

class IncidentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.cinema = Cinema.objects.create(nom="Paris", adresse="1 rue test", cp="75000", ville="Paris", pays="France", telephone="0102030405")
        self.qualite = Qualite.objects.create(type_qualite="Standard", prix_seance=10.0)
        self.salle = Salle.objects.create(numero_salle="1", total_places=100, qualite=self.qualite, cinema=self.cinema)
        self.siege = Siege.objects.create(salle=self.salle, numero_siege=1)

        self.employe = Utilisateur.objects.create_user(
            email='employe@example.com',
            password='motdepasse',
            nom='Test',
            prenom='Employé',
            is_staff=True
        )
        self.token, _ = Token.objects.get_or_create(user=self.employe)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_incident(self):
        payload = {
            "salle": self.salle.id,
            "siege": self.siege.id,
            "type_incident": "Siège cassé",
            "type_materiel": "siège",
            "description": "Le siège est cassé."
        }
        response = self.client.post(reverse('api_incident_list_create'), payload, format='json')
        print("Réponse erreur:", response.status_code, response.data)  # Ajouté pour debug
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Incident.objects.count(), 1)

    def test_get_incidents_list(self):
        Incident.objects.create(
            utilisateur=self.employe,
            salle=self.salle,
            siege=self.siege,
            type_incident="Lumière",
            type_materiel="Éclairage",
            description="Lumière grillée"
        )
        response = self.client.get(reverse('api_incident_list_create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_resolve_incident(self):
        incident = Incident.objects.create(
            utilisateur=self.employe,
            salle=self.salle,
            siege=self.siege,
            type_incident="Écran fissuré",
            type_materiel="Écran",
            description="Petite fissure visible"
        )
        url = reverse('api_incident_resolve', args=[incident.id])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['statut'], 'Résolu')
