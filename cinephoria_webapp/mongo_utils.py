from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import certifi
from django.http import HttpResponse
from django.shortcuts import render

def get_mongo_collection():
    try:
        mongo_uri = os.environ["MONGO_URI"]
        client = MongoClient(
            mongo_uri,
            tls=True,
            tlsCAFile=certifi.where()
        )
        db = client["cinephoria_db"]
        return db["reservation_stats"]
    except Exception as e:
        print(f"[MongoDB ERROR] {e}")
        return None

def get_reservations_last_7_days():
    collection = get_mongo_collection()
    if collection is None:
        return []  

    date_limite = datetime.now() - timedelta(days=7)
    pipeline = [
        {"$match": {"date": {"$gte": date_limite}}},
        {"$group": {"_id": "$film_titre", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]

    try:
        return list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"[MongoDB ERROR] Échec de l'agrégation : {e}")
        return []



def admin_panel(request):
    try:
        reservations = get_reservations_last_7_days()
        print("[DEBUG] Réservations MongoDB :", reservations)  
        return render(request, 'admin/dashboard.html', {"reservations": reservations})
    except Exception as e:
        print("[ERROR] Échec chargement admin panel :", e)
        return HttpResponse("Erreur admin panel", status=500)