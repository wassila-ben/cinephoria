from rest_framework import serializers
from .models import Incident, Salle, Siege

class IncidentSerializer(serializers.ModelSerializer):
    utilisateur_email = serializers.EmailField(source='utilisateur.email', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'utilisateur', 'utilisateur_email',
            'salle', 'siege',
            'type_incident', 'type_materiel',
            'description', 'date', 'statut'
        ]
        read_only_fields = ['utilisateur', 'date', 'statut']
