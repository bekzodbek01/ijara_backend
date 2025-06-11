
from rest_framework import serializers

from house.models import House


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ['id', 'image', 'price', 'address', 'room_count', 'description', 'views_count',]

