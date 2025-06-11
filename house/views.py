from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import House
from .permission import IsOwner, IsFaceVerified
from .serializers import HouseSerializer

# Barcha uyni ko‘rish (filter district orqali)
class HouseListView(generics.ListAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]  # login bo‘lsa yetarli

    def get_queryset(self):
        queryset = super().get_queryset()
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district__iexact=district)
        return queryset

# Uy haqida batafsil
class HouseDetailView(generics.RetrieveAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]  # login bo‘lsa yetarli

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

# Uy egasi uyi qo‘shadi
class HouseCreateView(generics.CreateAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated, IsFaceVerified]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Tahrirlash va o‘chirish
class HouseUpdateView(generics.UpdateAPIView):
    serializer_class = HouseSerializer
    queryset = House.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return House.objects.filter(owner=self.request.user)

class HouseDeleteView(generics.DestroyAPIView):
    queryset = House.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return House.objects.filter(owner=self.request.user)
