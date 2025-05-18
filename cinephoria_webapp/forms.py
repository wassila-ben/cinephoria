from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur, Seance, Reservation, ReservationSiege, Siege
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

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['seance', 'nombre_places']

class SiegeSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        seance = kwargs.pop('seance', None)
        super().__init__(*args, **kwargs)
        if seance:
            # Filtrer les sièges libres pour cette séance
            reserved_sieges = ReservationSiege.objects.filter(reservation__seance=seance).values_list('siege_id', flat=True)
            sieges_disponibles = Siege.objects.exclude(id__in=reserved_sieges)

            self.fields['sieges'] = forms.ModelMultipleChoiceField(
                queryset=sieges_disponibles,
                widget=forms.CheckboxSelectMultiple,
                required=True,
                label="Choisissez vos sièges"
            )