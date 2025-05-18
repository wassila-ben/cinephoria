from django.core.management.base import BaseCommand
from cinephoria_webapp.models import Cinema, Salle, Siege, Genre, Film, Qualite, Seance
from django.utils import timezone
from datetime import datetime, timedelta, time
import random

class Command(BaseCommand):
    help = "Peuple la base de données avec des données de démonstration"

    def handle(self, *args, **kwargs):
        villes_fr = ["Paris", "Nantes", "Toulouse", "Bordeaux", "Lille"]
        villes_be = ["Charleroi", "Liège"]
        films = [
            "Code zéro", "Cœur à Contretemps", "Confusion Totale", "Divorce et Ricochets",
            "La Forêt des Murmures", "Le Masque du Revenant", "Le Royaume Caché", "Le Voyage des Cœurs Vaillants",
            "Les Enfants de l’Hyperespace", "Les Vacances de Tonton Gaston", "Opération Blackout",
            "Planète Mars", "Startup en Délire", "Tatie Déraille"
        ]
        qualites = ["4K", "3D", "4DX"]
        genres = ["Science-fiction", "Comédie", "Romance", "Horreur", "Aventure", "Drame", "Animation"]

        # Création des qualités
        qualite_objs = []
        for q in qualites:
            obj, _ = Qualite.objects.get_or_create(type_qualite=q, defaults={"prix_seance": random.uniform(8, 16)})
            qualite_objs.append(obj)

        # Création des genres
        genre_objs = []
        for g in genres:
            obj, _ = Genre.objects.get_or_create(genre=g)
            genre_objs.append(obj)

        # Création des cinémas
        for ville in villes_fr + villes_be:
            pays = "France" if ville in villes_fr else "Belgique"
            cinema, _ = Cinema.objects.get_or_create(
                nom=f"Cinéphoria {ville}",
                ville=ville,
                pays=pays,
                adresse="1 place centrale",
                cp="75000",
                telephone="01 23 45 67 89"
            )
            self.stdout.write(self.style.SUCCESS(f"🎬 Cinéma créé : {cinema.nom}"))

            # Salles
            for i in range(1, 11):
                qualite = random.choice(qualite_objs)
                salle = Salle.objects.create(
                    numero_salle=str(i),
                    total_places=165,
                    places_pmr=random.randint(10, 15),
                    qualite=qualite,
                    Cinema=cinema
                )
                # Sièges
                for num in range(1, 151):
                    salle.sieges.create(numero_siege=num, rangee=chr(65 + (num // 15)), place_pmr=False)
                for num in range(151, 151 + salle.places_pmr):
                    salle.sieges.create(numero_siege=num, rangee='PMR', place_pmr=True)

        # Films
        for titre in films:
            genre = random.choice(genre_objs)
            Film.objects.get_or_create(
                titre=titre,
                genre=genre,
                note=random.uniform(1.0, 5.0),
                age_minimum=random.choice([0, 7, 12, 16]),
                synopsis="Synopsis automatique généré pour la démo.",
                date_sortie=timezone.now().date(),
                affiche="films/default.jpg",  
            )
        self.stdout.write(self.style.SUCCESS("Films et genres ajoutés !"))

        self.stdout.write(self.style.SUCCESS("Base de données de démonstration prête !"))


def create_seances():
    print("\n Création des séances...")
    horaires_possibles = [
        time(10, 0), time(13, 0), time(15, 30),
        time(18, 0), time(20, 30), time(22, 0)
    ]

    for cinema in Cinema.objects.all():
        salles = cinema.salles.all()
        films_cinema = Film.objects.filter(seance__salle__cinema=cinema).distinct()

        if not films_cinema:
            # Si aucun film n'est associé à ce cinéma, on prend quelques films au hasard
            films_cinema = Film.objects.order_by('?')[:5]

        for salle in salles:
            nb_seances = random.randint(2, 3)
            horaires = random.sample(horaires_possibles, nb_seances)

            for h in horaires:
                film = random.choice(films_cinema)
                duree = timedelta(minutes=random.randint(90, 150))
                heure_fin = (datetime.combine(datetime.today(), h) + duree).time()

                Seance.objects.create(
                    film=film,
                    salle=salle,
                    heure_debut=h,
                    heure_fin=heure_fin
                )

    print("Séances créées avec succès.")