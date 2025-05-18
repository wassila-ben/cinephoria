from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# Connexion à MongoDB (adaptée à Docker)
client = MongoClient("mongodb://mongo:27017/")
db = client["cinephoria"]
collection = db["reservation_stats"]

# Vide la collection avant d'insérer de nouvelles données
collection.delete_many({})

# Films fictifs
films = [
    "Le Dernier Astronaute",
    "L'Ombre du Phare",
    "VirtuaZ", 
    "Résistance 2049",
    "Les Chroniques de Veralis",
    "Echo Zéro",
    "Les Gardiens de l'Oubli",
    "Cendres du Futur"
]

# Insertion de 300 réservations réparties aléatoirement sur 7 jours
for _ in range(300):
    film = random.choice(films)
    jours_aleatoire = random.randint(0, 6)
    date_reservation = datetime.now() - timedelta(days=jours_aleatoire)

    collection.insert_one({
        "film_titre": film,
        "date": date_reservation
    })

print(" Données de test MongoDB injectées.")
