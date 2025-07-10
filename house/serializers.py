from rest_framework import serializers
from .models import House, House_image, Region, District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class RegionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'name', 'districts']


class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = House_image
        fields = ['id', 'image']


class HouseSerializer(serializers.ModelSerializer):
    images = HouseImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    is_saved = serializers.SerializerMethodField()


    class Meta:
        model = House
        fields = [
            'id', 'title', 'price', 'region', 'district', 'room_count', 'description',
            'views_count', 'images', 'uploaded_images', 'is_saved',
        ]

    def get_is_saved(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.saved_by.filter(id=user.id).exists()
        return False


    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        house = House.objects.create(**validated_data)

        for image in uploaded_images:
            House_image.objects.create(house=house, image=image)

        return house
