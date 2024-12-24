import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from datetime import date
import os

# Rôle des utilisateurs
class Role(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True, default="Aucune description")

    def __str__(self):
        return self.nom


# Utilisateur
class Utilisateur(models.Model):
    identifiant = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=50, default="Nom inconnu")
    prenom = models.CharField(max_length=50, default="Prénom inconnu")
    email = models.EmailField(unique=True)
    mdp = models.CharField(max_length=100)  # Mot de passe hashé
    pays = models.CharField(max_length=50, default="France")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.identifiant


# Notifications
class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255, default="Aucune notification")
    date = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification pour {self.utilisateur or 'Tous'} : {self.message}"


# Genre de film
class Genre(models.Model):
    genre = models.CharField(max_length=50, default="Inconnu")

    def __str__(self):
        return self.genre


# Film
class Film(models.Model):
    titre = models.CharField(max_length=100, default="Titre inconnu")
    synopsis = models.TextField(default="Synopsis indisponible")
    affiche = models.ImageField(upload_to='films/', default='default/affiche.jpg')
    date_ajout = models.DateField(default=date.today)
    age_minimum = models.IntegerField(default=0)
    label_coup_de_coeur = models.BooleanField(default=False)
    note = models.FloatField(default=0.0)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    dernier_modificateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='modifications')
    date_derniere_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


# Qualité
class Qualite(models.Model):
    type_qualite = models.CharField(max_length=50, default="Standard")
    prix_seance = models.FloatField(default=10.0)
    logo_qualite = models.ImageField(upload_to='logos/', default='default/logo.png')

    def __str__(self):
        return self.type_qualite


# Salle
class Salle(models.Model):
    numero_salle = models.CharField(max_length=10, default="1")
    nombre_places = models.IntegerField(default=100)
    places_pmr = models.IntegerField(default=10)
    qualite = models.ForeignKey(Qualite, on_delete=models.CASCADE)

    def __str__(self):
        return self.numero_salle


# Siège
class Siege(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    numero_siege = models.CharField(max_length=10, default="A1")
    rangee = models.CharField(max_length=10, default="A")
    libre = models.BooleanField(default=True)
    place_pmr = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.salle.numero_salle} - {self.numero_siege}"


# Séance
class Seance(models.Model):
    heure_debut = models.TimeField(default="20:30")
    heure_fin = models.TimeField(default="22:00")
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.film.titre} - {self.heure_debut}"


# Cinéma
class Cinema(models.Model):
    nom = models.CharField(max_length=100, default="Cinéma inconnu")
    adresse = models.TextField(default="1 place des étoiles")
    cp = models.CharField(max_length=10, default="75000")
    ville = models.CharField(max_length=50, default="Paris")
    pays = models.CharField(max_length=50, default="France")
    telephone = models.CharField(max_length=20, default="01 23 45 67 89")
    horaire_ouverture = models.TimeField(default="10:00")
    horaire_fermeture = models.TimeField(default="23:00")
    seances = models.ManyToManyField(Seance)

    def __str__(self):
        return self.nom


# Réservation
class Reservation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_reservation = models.DateField(auto_now_add=True)
    nombre_places = models.IntegerField(default=1)
    prix_total = models.FloatField(default=0.0)

    def __str__(self):
        return f"Réservation {self.id} - {self.utilisateur}"


# Réservation de siège
class ReservationSiege(models.Model):
    siege = models.ForeignKey(Siege, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Réservation siège {self.siege.numero_siege}"


# Statut de réservation
class StatutReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    statut = models.CharField(max_length=50, default="En attente")

    def __str__(self):
        return f"Statut de {self.reservation}"


# billet
class Billet(models.Model):
    reservation = models.ForeignKey('Reservation', on_delete=models.CASCADE)
    numero_billet = models.CharField(max_length=20, unique=True, default="000000")
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    def __str__(self):
        return f"Billet {self.numero_billet} - {self.reservation.utilisateur.identifiant}"

    def generate_qr_code(self):
        # Récupérer les détails nécessaires pour le QR code
        seance = self.reservation.siege_set.first().salle.seance_set.first()
        film_titre = seance.film.titre if seance else "Film inconnu"
        numero_salle = seance.salle.numero_salle if seance else "Salle inconnue"
        numero_siege = self.reservation.siege_set.first().numero_siege if self.reservation.siege_set.exists() else "Siège inconnu"
        heure_seance = seance.heure_debut.strftime("%H:%M") if seance else "Heure inconnue"

        # Contenu du QR code
        qr_data = (
            f"Titre du film: {film_titre}\n"
            f"Numéro de salle: {numero_salle}\n"
            f"Numéro de siège: {numero_siege}\n"
            f"Heure de la séance: {heure_seance}"
        )

        # Génération du QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Création de l'image
        img = qr.make_image(fill_color="black", back_color="white")

        # Sauvegarde dans un fichier
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_code_billet_{self.numero_billet}.png"

        # Enregistrement de l'image dans le champ `qr_code`
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        # Générer le QR code avant de sauvegarder
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Supprimer le fichier de QR code associé
        if self.qr_code and os.path.isfile(self.qr_code.path):
            os.remove(self.qr_code.path)
        super().delete(*args, **kwargs)



# Avis
class Avis(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    note = models.FloatField(default=0.0)
    commentaire = models.TextField(default="Pas de commentaire")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Avis de {self.utilisateur.identifiant} sur {self.film.titre}"


# Historisation des actions
class LogActivite(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, default="Action inconnue")
    date = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Action de {self.utilisateur.identifiant} : {self.action} ({self.date})"


# Incidents
class Incident(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    siege = models.ForeignKey(Siege, on_delete=models.CASCADE)
    type_incident = models.CharField(max_length=100, default="Type inconnu")
    type_materiel = models.CharField(max_length=100, default="Matériel inconnu")
    description = models.TextField(default="Description non disponible")
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="Ouvert")

    def __str__(self):
        return f"Incident {self.type_incident} - {self.utilisateur.identifiant}"

# Contact
class Contact(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, blank=True, default="Anonyme")
    objet_demande = models.CharField(max_length=100, default="Objet inconnu")
    description = models.TextField(default="Pas de description")
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="En attente")

    def __str__(self):
        return f"Contact {self.nom or 'Anonyme'} - {self.objet_demande}"
