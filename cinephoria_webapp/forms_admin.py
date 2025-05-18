from django import forms
from .models import Film, Seance, Salle, Utilisateur
from django.contrib.auth.forms import UserCreationForm

class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        exclude = ['note', 'dernier_modificateur', 'date_derniere_modification']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'duree': forms.NumberInput(attrs={'class': 'form-control'}),
            'synopsis': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'date_ajout': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_sortie': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'age_minimum': forms.NumberInput(attrs={'class': 'form-control'}),
            'label_coup_de_coeur': forms.CheckboxInput(attrs={'class': 'form-check-input mt-1'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'cinemas': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 4}),
            'affiche': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = '__all__'
        widgets = {
            'film': forms.Select(attrs={'class': 'form-select'}),
            'salle': forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'jours_diffusion': forms.SelectMultiple(
                attrs={'class': 'form-select', 'size': 5}
            ),
        }


class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = '__all__'
        widgets = {
            'numero_salle': forms.TextInput(attrs={'class': 'form-control'}),
            'total_places': forms.NumberInput(attrs={'class': 'form-control'}),
            'places_pmr': forms.NumberInput(attrs={'class': 'form-control'}),
            'qualite': forms.Select(attrs={'class': 'form-select'}),
            'cinema': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['email', 'identifiant', 'nom', 'prenom', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # Employé ≠ superutilisateur
        user.is_superuser = False
        if commit:
            user.save()
        return user
    
class ResetEmployePasswordForm(forms.Form):
    employe = forms.ModelChoiceField(
        queryset=Utilisateur.objects.filter(is_staff=True, is_superuser=False),
        label="Employé",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nouveau_mot_de_passe = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmation_mot_de_passe = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    def clean(self):
        cleaned_data = super().clean()
        nouveau_mot_de_passe = cleaned_data.get("nouveau_mot_de_passe")
        confirmation_mot_de_passe = cleaned_data.get("confirmation_mot_de_passe")

        if nouveau_mot_de_passe != confirmation_mot_de_passe:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data
    def save(self, commit=True):
        employe = self.cleaned_data.get('employe')
        nouveau_mot_de_passe = self.cleaned_data.get('nouveau_mot_de_passe')
        employe.set_password(nouveau_mot_de_passe)
        if commit:
            employe.save()
        return employe