from django.contrib import admin
from .models import (
    Genre, Film, Utilisateur, Role, Notification, Qualite,
    Salle, Siege, Seance, Cinema, Reservation, ReservationSiege,
    StatutReservation, Billet, Avis, LogActivite, Incident, Contact
)


# Modèle Genre
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre')
    search_fields = ('genre',)


# Modèle Film
@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'genre', 'note', 'date_ajout', 'dernier_modificateur')
    search_fields = ('titre', 'genre__genre')
    list_filter = ('genre', 'label_coup_de_coeur')
    readonly_fields = ('date_ajout', 'date_derniere_modification')


# Modèle Utilisateur
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'identifiant', 'nom', 'prenom', 'email', 'role')
    search_fields = ('identifiant', 'email', 'nom')
    list_filter = ('role',)


# Modèle Rôle
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'description')
    search_fields = ('nom',)


# Modèle Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'message', 'date', 'lue')
    search_fields = ('message', 'utilisateur__identifiant')
    list_filter = ('lue',)


# Modèle Qualité
@admin.register(Qualite)
class QualiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_qualite', 'prix_seance')
    search_fields = ('type_qualite',)


# Modèle Salle
@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_salle', 'nombre_places', 'places_pmr', 'qualite')
    search_fields = ('numero_salle',)
    list_filter = ('qualite',)


# Modèle Siège
@admin.register(Siege)
class SiegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'salle', 'numero_siege', 'rangee', 'libre', 'place_pmr')
    search_fields = ('salle__numero_salle', 'numero_siege')
    list_filter = ('libre', 'place_pmr')


# Modèle Séance
@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'film', 'salle', 'heure_debut', 'heure_fin')
    search_fields = ('film__titre', 'salle__numero_salle')
    list_filter = ('film', 'salle')


# Modèle Cinéma
@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'ville', 'pays', 'horaire_ouverture', 'horaire_fermeture')
    search_fields = ('nom', 'ville')
    list_filter = ('pays',)


# Modèle Réservation
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'date_reservation', 'nombre_places', 'prix_total')
    search_fields = ('utilisateur__identifiant',)
    list_filter = ('date_reservation',)


# Modèle Réservation de siège
@admin.register(ReservationSiege)
class ReservationSiegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'siege', 'reservation')
    search_fields = ('siege__numero_siege', 'reservation__id')


# Modèle Statut de réservation
@admin.register(StatutReservation)
class StatutReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'statut')
    search_fields = ('reservation__id', 'statut')


# Modèle Billet
@admin.register(Billet)
class BilletAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'numero_billet', 'qr_code')
    search_fields = ('numero_billet', 'reservation__id')


# Modèle Avis
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'film', 'note', 'date')
    search_fields = ('utilisateur__identifiant', 'film__titre')
    list_filter = ('note',)


# Modèle LogActivite
@admin.register(LogActivite)
class LogActiviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'action', 'date')
    search_fields = ('utilisateur__identifiant', 'action')
    list_filter = ('date',)


# Modèle Incident
@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'siege', 'type_incident', 'statut', 'date')
    search_fields = ('utilisateur__identifiant', 'siege__numero_siege', 'type_incident')
    list_filter = ('statut', 'date')


# Modèle Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'cinema', 'objet_demande', 'statut', 'date')
    search_fields = ('utilisateur__identifiant', 'cinema__nom', 'objet_demande')
    list_filter = ('statut', 'date')
