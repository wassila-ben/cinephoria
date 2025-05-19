from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from .models import Reservation
from cinephoria_webapp.mongo_utils import get_mongo_collection
from django.conf import settings
from rest_framework.authtoken.models import Token
from .models import Utilisateur


@receiver(post_save, sender=Reservation)
def ajouter_reservation_mongo(sender, instance, created, **kwargs):
    if created:
        try:
            collection = get_mongo_collection()
            collection.insert_one({
                "film_titre": instance.seance.film.titre,
                "date": datetime.now()
            })
            print("Réservation synchronisée avec BDD Mongo")
        except Exception as e:
            print(f"Erreur MongoDB : {e}")

@receiver(post_save, sender=Utilisateur)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)