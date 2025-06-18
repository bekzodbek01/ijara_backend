from rest_framework import serializers
from .models import House, House_image


class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = House_image
        fields = ['id', 'image']


class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = House
        fields = [
            'id', 'price', 'address', 'room_count', 'description',
            'views_count', 'images', 'uploaded_images'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        house = House.objects.create(**validated_data)

        for image in uploaded_images:
            House_image.objects.create(house=house, image=image)

        return house
