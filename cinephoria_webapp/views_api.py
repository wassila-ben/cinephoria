from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import obtain_auth_token

from .models import Incident, Salle
from .serializers import IncidentSerializer

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
