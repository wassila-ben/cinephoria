# cinephoria

# Cinéphoria

Cinéphoria est une chaine de cinéma en Franc et en Belgique. Le site de l'enseigne permet la réservation de billets de cinéma sur une plateforme moderne et écoresponsable.  
Cette plateforme permet aux utilisateur et/ou visiteurs, de consulter les films à l'affiche, les séances, de reserver des places; et aux employés de gérer les salles, séances et incidents.

## Technologies utilisées

- Python 3.10
- Django 5.1.7
- PostgreSQL
- Docker & Docker Compose
- Cloudinary (stockage des médias)
- MongoDB (pour le dashboard)
- Bootstrap 5
- ElectronJS (client bureautique) & npm
- API REST (DRF)
- Heroku pour le déploiement en production

---

## Application Web
- Navigation par film, séance, cinéma
- Réservation avec sélection de sièges (PMR incluse)
- Connexion utilisateur / création de compte
- Espace personnel (QR code, historique, notation de films)
- Système d’avis avec validation par un employé

### Intranet Employé
- Création, modification et suppression de films, séances, salles
- Modération des avis

### Application Bureautique
- Saisie et consultation des incidents matériels (sièges, écrans…)

### Administration
- Gestion des comptes employés
- Dashboard (statistiques MongoDB)
- Réinitialisation des mots de passe employés

## Lancer l’application en local

### 1. Cloner le dépôt

```bash
git clone https://github.com/wassila-ben/cinephoria.git
cd cinephoria
```

### 2. Configurer les variables d’environnement

Créer un fichier `.env` à la racine du projet comme dans cet exemple:

```env
DEBUG=True
DJANGO_ENV=dev
DJANGO_SETTINGS_MODULE=cinephoria_app.settings.dev
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=cinema
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
DATABASE_URL=postgres://admin:admin123@db:5432/cinema
MONGO_URL=mongodb://...
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

### 3. Lancer avec Docker

```bash
docker-compose up -d --build
```

Accès :
- http://localhost:8000

---

### 4. Commandes utiles

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py loaddata initial_data.json
```

---


## 📂 Structure du projet
- `cinephoria_app/` : backend/settings
- `cinephoria_webapp/` : App principale / Web
- `templates/` : templates HTML
- `static/` : CSS/JS/logos
- `electron_app/` : application bureautique (ElectronJS)
- `api/` : endpoints REST (DRF)
- `tests/` : tests unitaires & fonctionnels

---

Le déploiement en production est disponible sur Heroku.
Voir les instructions détaillées dans la documentation technique dans /docs/Documentation_technique.pdf


