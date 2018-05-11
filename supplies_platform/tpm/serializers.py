
from rest_framework import serializers
from .models import TPMVisit


class TPMVisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = TPMVisit
        fields = '__all__'
