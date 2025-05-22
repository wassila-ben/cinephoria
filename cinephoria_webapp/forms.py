from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur, Seance, Reservation, ReservationSiege, Siege, Avis, Film, Cinema, Contact
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    nom = forms.CharField(max_length=100)
    prenom = forms.CharField(max_length=100)
    pays = forms.CharField(max_length=100)

    class Meta:
        model = Utilisateur  # Modele utilisateur personnalisé
        fields = ('email', 'nom', 'prenom', 'pays', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

Utilisateur = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(label="Mot de passe", strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    class Meta:
        model = Utilisateur
        fields = ('email', 'password')

class SeanceForm(forms.ModelForm):
    jours_diffusion = forms.MultipleChoiceField(
        choices=Seance.JOURS_SEMAINE,
        widget=forms.CheckboxSelectMultiple,
        label="Jours de diffusion"
    )

    class Meta:
        model = Seance
        fields = '__all__'


class ChoixSeanceForm(forms.Form):
    seance = forms.ModelChoiceField(queryset=Seance.objects.select_related('film', 'salle__cinema'), label="Sélectionnez une séance")


class ReservationForm(forms.Form):
    film = forms.ModelChoiceField(
        queryset=Film.objects.all(),
        label="Film",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_film'})
    )

    cinema = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'id': 'id_cinema'}))
    jour = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'id': 'id_jour'}))
    heure = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'id': 'id_heure'}))

    nombre_places = forms.IntegerField(
        label="Nombre de places",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    places_pmr = forms.BooleanField(
        label="Places PMR",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class SiegeSelectionForm(forms.Form):
    sieges = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.seance = kwargs.pop('seance', None)
        self.places_pmr = kwargs.pop('places_pmr', False)  # ✅ ici
        super().__init__(*args, **kwargs)

    def clean_sieges(self):
        ids_str = self.cleaned_data['sieges']
        try:
            ids = [int(i) for i in ids_str.split(',') if i.strip()]
        except ValueError:
            raise ValidationError("Format invalide pour les sièges.")

        sieges_qs = Siege.objects.filter(id__in=ids)

        if sieges_qs.count() != len(ids):
            raise ValidationError("Un ou plusieurs sièges sélectionnés sont invalides.")

        if self.seance:
            sieges_salle = set(self.seance.salle.sieges.values_list('id', flat=True))
            if not all(s.id in sieges_salle for s in sieges_qs):
                raise ValidationError("Certains sièges ne sont pas dans la salle de cette séance.")

        # Vérifie la sélection PMR
        pmr_count = sum(1 for s in sieges_qs if s.place_pmr)

        if self.places_pmr:
            if pmr_count == 0:
                raise ValidationError("Vous avez demandé des places PMR, mais aucun siège PMR n'a été sélectionné.")
        else:
            if pmr_count > 0:
                raise ValidationError("Vous n'avez pas demandé de place PMR, mais vous en avez sélectionné une.")

        return sieges_qs


class AvisForm(forms.ModelForm):
    NOTE_CHOICES = [(i, f"{'★' * i}") for i in range(1, 6)]

    note = forms.ChoiceField(
        choices=NOTE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Note"
    )

    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class SeanceSelectorForm(forms.Form):
    film = forms.ModelChoiceField(
        queryset=Film.objects.all(),
        label="Film",
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    cinema = forms.ModelChoiceField(
        queryset=Cinema.objects.none(),  # Initialement vide
        label="Cinéma",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    jour = forms.DateField(
        required=False,
        label="Jour",
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )

    heure = forms.TimeField(
        required=False,
        label="Heure",
        widget=forms.TimeInput(attrs={
            "type": "time",
            "class": "form-control"
        })
    )

class MotDePasseOublieForm(forms.Form):
    email = forms.EmailField(label="Adresse email", widget=forms.EmailInput(attrs={'class': 'form-control'}))

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'cinema', 'objet_demande', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'cinema': forms.Select(attrs={'class': 'form-select'}),
            'objet_demande': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }

    def clean_objet_demande(self):
        value = self.cleaned_data.get('objet_demande', '').strip()
        if not value or value == "Objet inconnu":
            raise forms.ValidationError("L’objet est requis.")
        return value

    def clean_description(self):
        value = self.cleaned_data.get('description', '').strip()
        if not value or value == "Pas de description":
            raise forms.ValidationError("La description est obligatoire.")
        return value
