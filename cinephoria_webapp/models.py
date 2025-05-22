from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os
import qrcode
import uuid

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

# Custom user model
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    identifiant = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nom = models.CharField(max_length=50, default="Nom inconnu")
    prenom = models.CharField(max_length=50, default="Prénom inconnu")
    ville = models.CharField(max_length=50, default="Paris")
    pays = models.CharField(max_length=50, default="France")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    

    groups = models.ManyToManyField(
        Group,
        related_name="utilisateur_groups",
        blank=True,
        verbose_name="groupes"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="utilisateur_permissions",
        blank=True,
        verbose_name="autorisations utilisateur"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    def __str__(self):
        return self.email

class Role(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True, default="Aucune description")

    def __str__(self):
        return self.nom

class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255, default="Aucune notification")
    date = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification pour {self.utilisateur or 'Tous'} : {self.message}"

class Genre(models.Model):
    genre = models.CharField(max_length=50, default="Inconnu")

    def __str__(self):
        return self.genre

class Film(models.Model):
    titre = models.CharField(max_length=100, default="Titre inconnu")
    duree = models.PositiveIntegerField(default=90,help_text="Durée en minutes")
    synopsis = models.TextField(default="Synopsis indisponible")
    affiche = models.ImageField(upload_to='films/', null=True, blank=True, max_length=300)
    affiche_url = models.URLField(null=True, blank=True)
    date_ajout = models.DateField(null=True, blank=True)
    date_sortie = models.DateField(null=True, blank=True)
    age_minimum = models.IntegerField(default=0)
    label_coup_de_coeur = models.BooleanField(default=False)
    note = models.FloatField(default=0.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    cinemas = models.ManyToManyField('Cinema', related_name='films')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    dernier_modificateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='modifications')
    date_derniere_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    def calculer_note_moyenne(self):
        avis = self.avis.all()
        moyenne = avis.aggregate(models.Avg('note'))['note__avg'] or 0
        self.note = moyenne
        self.save()

class Qualite(models.Model):
    type_qualite = models.CharField(max_length=50, default="Standard")
    prix_seance = models.FloatField(default=10.0)
    logo_qualite = models.ImageField(upload_to='logos/', default='default/logo.png')

    def __str__(self):
        return self.type_qualite

class Salle(models.Model):
    numero_salle = models.CharField(max_length=2, default="0")
    total_places = models.PositiveIntegerField()
    places_pmr = models.PositiveIntegerField(default=0)
    qualite = models.ForeignKey(Qualite, on_delete=models.CASCADE)
    cinema = models.ForeignKey('Cinema', on_delete=models.CASCADE, related_name='salles')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generer_sieges()

    def generer_sieges(self):
        RANGEES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        sieges_max_par_rangee = 10
        pmr_ratio = 0.05

        total_places = self.total_places
        pmr_places = self.places_pmr or int(total_places * pmr_ratio)

        count = 0
        pmr_assigned = 0
        rangee_index = 0

        while count < total_places:
            current_rangee = RANGEES[rangee_index % len(RANGEES)]
            for num in range(1, sieges_max_par_rangee + 1):
                if count >= total_places:
                    break

                is_pmr = pmr_assigned < pmr_places
                if is_pmr:
                    pmr_assigned += 1

                Siege.objects.create(
                    salle=self,
                    numero_siege=num,
                    rangee=current_rangee,
                    place_pmr=is_pmr
                )
                count += 1
            rangee_index += 1

    def __str__(self):
        return f"Salle {self.numero_salle} - {self.cinema.nom}"
    
class Seance(models.Model):
    JOURS_SEMAINE = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    film = models.ForeignKey('Film', on_delete=models.CASCADE)
    salle = models.ForeignKey('Salle', on_delete=models.CASCADE)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField(blank=True, null=True)
    jours_diffusion = models.JSONField(default=list, help_text="Liste des jours (ex: [0, 2, 4])")

    def __str__(self):
        jours = ", ".join([self.get_jour_display(j) for j in self.jours_diffusion])
        return f"{self.film.titre} - {jours} à {self.heure_debut.strftime('%H:%M')}"

    def get_jour_display(self, jour_index):
        return dict(self.JOURS_SEMAINE).get(jour_index, "Jour inconnu")

    def save(self, *args, **kwargs):
        if not self.heure_fin:
            debut_dt = datetime.combine(datetime.today(), self.heure_debut)
            fin_dt = debut_dt + timedelta(minutes=self.film.duree)
            self.heure_fin = fin_dt.time()
        super().save(*args, **kwargs)

    def prix(self):
        return self.salle.qualite.prix_seance

    def qualite(self):
        return self.salle.qualite.type_qualite

    def cinema(self):
        return self.salle.cinema
    
    def get_jours_affichage(self):
        jours_dict = dict(self.JOURS_SEMAINE)
        return [jours_dict.get(j, "Inconnu") for j in self.jours_diffusion]


class Siege(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name="sieges")
    numero_siege = models.PositiveBigIntegerField()
    rangee = models.CharField(max_length=10, default="A")
    occupe = models.BooleanField(default=False)
    place_pmr = models.BooleanField(default=False)

    def __str__(self):
        return f"Salle {self.salle.numero_salle} - Siege {self.numero_siege}"


class Cinema(models.Model):
    nom = models.CharField(max_length=100, default="Cinéma inconnu")
    adresse = models.TextField(default="1 place des étoiles")
    cp = models.CharField(max_length=10, default="75000")
    ville = models.CharField(max_length=50, default="Paris")
    pays = models.CharField(max_length=50, default="France")
    telephone = models.CharField(max_length=20, default="01 23 45 67 89")
    horaire_ouverture = models.TimeField(default="10:00")
    horaire_fermeture = models.TimeField(default="23:00")

    def __str__(self):
        return self.nom
    
    def films_projetés(self):
        films = Film.objects.filter(seance__salle__cinema=self).distinct()
        return films

class Reservation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE)
    date_reservation = models.DateField(auto_now_add=True)
    nombre_places = models.IntegerField(default=1)
    prix_total = models.FloatField(default=0.0)
    statut = models.CharField(max_length=50, choices=[
        ('en attente', 'En attente'),
        ('confirmée', 'Confirmée'),
        ('annulée', 'Annulée'),
    ], default='en attente')
    
    def __str__(self):
        return f"Réservation {self.id} - {self.utilisateur} - {self.seance.film.titre} - {self.statut}"
    
    def calculer_prix(self):
        self.prix_total = self.nombre_places * self.seance.salle.qualite.prix_seance
        self.save()

class ReservationSiege(models.Model):
    siege = models.ForeignKey(Siege, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return f"Réservation siège {self.siege.numero_siege}"

class Billet(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='billet')

    
    def generate_unique_billet_number():
        return str(uuid.uuid4().hex[:10]).upper()

    numero_billet = models.CharField(max_length=20, unique=True, default=generate_unique_billet_number)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    def __str__(self):
        return f"Billet {self.numero_billet} - {self.reservation.utilisateur.identifiant}"

    def generate_qr_code(self):
        """Génère un QR code pour ce billet."""
        qr_data = (
            f"Réservation ID: {self.reservation.id}\n"
            f"Film: {self.reservation.seance.film.titre}\n"
            f"Salle: {self.reservation.seance.salle.numero_salle}\n"
            f"Heure: {self.reservation.seance.heure_debut}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Sauvegarde de l'image
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_code_billet_{self.numero_billet}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.qr_code and os.path.isfile(self.qr_code.path):
            os.remove(self.qr_code.path)
        super().delete(*args, **kwargs)



class Avis(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='avis')
    note = models.FloatField(default=1.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    commentaire = models.TextField(default='Pas de commentaire')
    date = models.DateField(auto_now_add=True)
    valide = models.BooleanField(default=False) 

    def __str__(self):
        return f"Avis de {self.utilisateur.identifiant} sur {self.film.titre}"

@receiver(post_save, sender=Avis)
@receiver(post_delete, sender=Avis)
def update_film_note_on_avis_change(sender, instance, **kwargs):
    instance.film.calculer_note_moyenne()

class LogActivite(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, default="Action inconnue")
    date = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Action de {self.utilisateur.identifiant} : {self.action} ({self.date})"

class Incident(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE,null=True, blank=True)  
    siege = models.ForeignKey(Siege, on_delete=models.SET_NULL, null=True, blank=True)  
    type_incident = models.CharField(max_length=100, default="Type inconnu")
    type_materiel = models.CharField(
        max_length=100,
        choices=[
            ('siège', 'Siège'),
            ('écran', 'Écran'),
            ('porte', 'Porte'),
            ('moquette', 'Moquette'),
            ('son', 'Son'),
            ('éclairage', 'Éclairage'),
            ('autre', 'Autre'),
        ],
        default='autre'
    )
    description = models.TextField(default="Description non disponible")
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="Ouvert")

    def __str__(self):
        cible = f"Siège {self.siege.numero_siege}" if self.siege else "Salle"
        return f"{self.type_incident} ({self.type_materiel}) - {cible}"


class Contact(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, blank=True, null=True)
    objet_demande = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="En attente")

    def __str__(self):
        return f"Contact {self.nom or 'Anonyme'} - {self.objet_demande}"

