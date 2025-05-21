from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import obtain_auth_token

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Incident, Salle, Film, Seance, Cinema, Reservation
from .serializers import IncidentSerializer
from datetime import datetime, timedelta
from django.db import models

# Vue pour l'authentification par token
token_auth_view = obtain_auth_token


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_incident_list_create(request):
    if request.method == 'GET':
        incidents = Incident.objects.select_related('utilisateur', 'siege__salle').all()
        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = IncidentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(utilisateur=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def api_incident_resolve(request, pk):
    try:
        incident = Incident.objects.get(pk=pk)
    except Incident.DoesNotExist:
        return Response({'detail': 'Incident non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    incident.statut = 'Résolu'
    incident.save()
    serializer = IncidentSerializer(incident)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_salles_list(request):
    salles = Salle.objects.select_related('cinema', 'qualite').all()
    data = [
        {
            'id': salle.id,
            'nom': f"{salle.cinema.nom} - Salle {salle.numero_salle}"
        } for salle in salles
    ]
    return Response(data)


@require_GET
def get_seance_infos(request):
    film_id = request.GET.get('film_id')
    data = {
        "cinemas": [],
        "jours": [],
        "horaires": []
    }

    if not film_id:
        return JsonResponse(data)

    try:
        film = Film.objects.get(id=film_id)
    except Film.DoesNotExist:
        return JsonResponse(data)

    today = datetime.today().date()
    horaires_set = set()
    jours_set = set()
    cinemas_set = set()

    # Toutes les séances à venir
    seances = Seance.objects.filter(film=film).select_related('salle__cinema', 'salle__qualite')

    for seance in seances:
        for jour_index in seance.jours_diffusion:
            jour_index = int(jour_index)  # 🔧 conversion nécessaire
            jour_date = today + timedelta((jour_index - today.weekday()) % 7)

            # Vérifie s'il reste des places
            total_places = seance.salle.total_places
            reserved = Reservation.objects.filter(seance=seance).aggregate(
                models.Sum("nombre_places")
            )["nombre_places__sum"] or 0

            if reserved >= total_places:
                continue

            cinemas_set.add(seance.salle.cinema)
            horaires_set.add(seance.heure_debut.strftime("%H:%M"))
            jours_set.add(jour_index)

    jours_map = {
        0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
        4: "Vendredi", 5: "Samedi", 6: "Dimanche"
    }

    for jour_index in sorted(jours_set):
        jour_index = int(jour_index)  # 🔧 à nouveau ici
        jour_date = today + timedelta((jour_index - today.weekday()) % 7)
        data["jours"].append({
            "label": f"{jours_map[jour_index]} {jour_date.strftime('%d/%m')}",
            "value": jour_date.isoformat()
        })

    data["cinemas"] = [{"id": c.id, "nom": c.nom} for c in cinemas_set]
    data["horaires"] = sorted(horaires_set)

    # Infos supplémentaires
    data["titre"] = film.titre
    data["synopsis"] = film.synopsis
    data["affiche"] = film.affiche.url if film.affiche else ""

    return JsonResponse(data)