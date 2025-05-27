from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Genre, Film, Utilisateur, Role, Notification, Qualite,
    Salle, Siege, Seance, Cinema, Reservation, ReservationSiege,
    Billet, Avis, LogActivite, Incident, Contact
)
from django import forms
from datetime import datetime,timedelta
from django.utils.timezone import now
from django.utils.html import format_html


# Modèle Genre
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre')
    search_fields = ('genre',)


# Modèle Film
@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'genre', 'date_ajout', 'dernier_modificateur')
    search_fields = ('titre', 'genre__genre')
    list_filter = ('genre', 'label_coup_de_coeur')
    readonly_fields = ('note','date_derniere_modification')


# Modèle Utilisateur
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'identifiant')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)



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
    list_display = ('id', 'numero_salle', 'total_places', 'places_pmr', 'qualite')
    search_fields = ('numero_salle','qualite__type_qualite')
    list_filter = ('qualite',)

# Modèle siège
@admin.register(Siege)
class SiegeAdmin(admin.ModelAdmin):
    list_display = ('salle', 'numero_siege', 'rangee', 'place_pmr', 'occupe_status')
    list_filter = ('salle', 'occupe', 'place_pmr')
    search_fields = ('numero_siege', 'salle__numero_salle')

    def occupe_status(self, obj):
        return "Libre" if not obj.occupe else "Occupé"
    occupe_status.short_description = "Disponibilité"



# Modèle Séance
class SeanceMultipleJourForm(forms.ModelForm):
    jours_semaine = forms.MultipleChoiceField(
        choices=Seance.JOURS_SEMAINE,
        widget=forms.CheckboxSelectMultiple,
        label="Jours de la semaine",
        required=False
    )

    class Meta:
        model = Seance
        fields = ['film', 'salle', 'heure_debut']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-remplir en cas de modification
        if self.instance and self.instance.pk:
            self.fields['jours_semaine'].initial = self.instance.jours_diffusion

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not cleaned_data.get('jours_semaine'):
            raise forms.ValidationError("Veuillez sélectionner au moins un jour pour créer une séance.")
        return cleaned_data


class SeanceAdmin(admin.ModelAdmin):
    form = SeanceMultipleJourForm
    readonly_fields = ('heure_fin',)
    list_display = ('film', 'salle', 'get_jours', 'heure_debut', 'heure_fin', 'get_prix')

    def get_jours(self, obj):
        return ', '.join(obj.get_jours_affichage())

    def get_prix(self, obj):
        if obj.salle and obj.salle.qualite:
            return f"{obj.salle.qualite.prix_seance} €"
        return "N/A"
    get_prix.short_description = 'Prix'

    def save_model(self, request, obj, form, change):
        jours = [int(j) for j in form.cleaned_data.get('jours_semaine', [])]

        if change:
            # MODIFICATION D'UNE SEANCE EXISTANTE
            if jours:
                obj.jours_diffusion = jours  
            else:
                obj.jours_diffusion = []  

            # Recalcul de l'heure de fin
            if obj.film and hasattr(obj.film, 'duree'):
                debut_dt = datetime.combine(datetime.today(), obj.heure_debut)
                fin_dt = debut_dt + timedelta(minutes=obj.film.duree)
                obj.heure_fin = fin_dt.time()

            super().save_model(request, obj, form, change)

        else:
            # CREATION – une séance par jour
            film = form.cleaned_data['film']
            salle = form.cleaned_data['salle']
            heure_debut = form.cleaned_data['heure_debut']

            for jour in jours:
                debut_dt = datetime.combine(datetime.today(), heure_debut)
                heure_fin = (debut_dt + timedelta(minutes=film.duree)).time()

                Seance.objects.create(
                    film=film,
                    salle=salle,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                    jours_diffusion=[jour]
            )

admin.site.register(Seance, SeanceAdmin)


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'ville', 'prochaines_seances')
    search_fields = ('nom', 'ville')
    list_filter = ('ville',)

    def prochaines_seances(self, obj):
        today_index = datetime.today().weekday()  # 0=lundi, 6=dimanche
        seances = Seance.objects.filter(
            salle__cinema=obj,
            jours_diffusion__contains=[today_index],
            heure_debut__gte=now().time()
        ).order_by('heure_debut')[:3]  # limite à 3 prochaines séances

        if not seances:
            return "Aucune séance aujourd’hui"

        return format_html(
            "<br>".join(
                f"{s.film.titre} à {s.heure_debut.strftime('%H:%M')} (Salle {s.salle.numero_salle})"
                for s in seances
            )
        )

    prochaines_seances.short_description = "Prochaines séances aujourd’hui"



# Modèle Réservation
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'seance', 'nombre_places', 'prix_total', 'statut')
    search_fields = ('utilisateur__email', 'seance__film__titre', 'statut')
    list_filter = ('statut',)
    ordering = ('-date_reservation',)

# Modèle Réservation de siège
@admin.register(ReservationSiege)
class ReservationSiegeAdmin(admin.ModelAdmin):
    list_display = ('id', 'siege', 'reservation')
    search_fields = ('siege__numero_siege', 'reservation__id')


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

