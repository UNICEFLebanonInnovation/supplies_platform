
from rest_framework import serializers
from .models import SMVisit


class SMVisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMVisit
        fields = '__all__'
