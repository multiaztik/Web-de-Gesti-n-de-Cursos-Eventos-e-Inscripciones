from rest_framework import serializers
from .models import Miembro

class MiembroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Miembro
        fields = ['id', 'nombre', 'correo', 'cursos', 'foto']
