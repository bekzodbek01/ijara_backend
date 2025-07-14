from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from .models import House, Region, District
from .permission import IsOwner, IsFaceVerified
from .serializers import HouseSerializer, RegionSerializer, DistrictSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import House_image


class HouseListView(generics.ListAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 1. Barcha active e'lonlar
        queryset = House.objects.filter(status='active', is_active=True)

        # 2. Agar Seller bo‘lsa, faqat o‘zining zakaslari
        if user.role == 'Seller':
            queryset = queryset.filter(owner=user)

        # 3. Tartiblash - ohirgi qo‘shilganlar birinchi bo‘lib chiqadi
        queryset = queryset.order_by('-created_at')

        # 4. Filtering query params orqali
        params = self.request.query_params

        region = params.get('region')
        district = params.get('district')
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        room_count = params.get('room_count')
        search = params.get('search')

        if region:
            if region.isdigit():
                queryset = queryset.filter(region__id=int(region))
            else:
                queryset = queryset.filter(region__name__iexact=region.strip())

        if district:
            if district.isdigit():
                queryset = queryset.filter(district__id=int(district))
            else:
                queryset = queryset.filter(district__name__iexact=district.strip())

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        if room_count:
            try:
                queryset = queryset.filter(room_count=int(room_count))
            except ValueError:
                pass

        if search:
            queryset = queryset.filter(title__icontains=search.strip())

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
        serializer.save(owner=self.request.user, status='pending', is_active=False)


class HousePublicListView(generics.ListAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return House.objects.filter(owner=user, status='active', is_active=True)


class MyDeactiveHouseListView(generics.ListAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return House.objects.filter(owner=self.request.user, status='deactive')


class HousePendingListView(generics.ListAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return House.objects.filter(owner=self.request.user, status='pending')


class ResendToAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        house_id = request.data.get("house_id")
        if not house_id:
            return Response({"detail": "house_id yuborilishi shart."}, status=400)

        try:
            house = House.objects.get(id=house_id, owner=request.user)
        except House.DoesNotExist:
            return Response({"detail": "E’lon topilmadi yoki sizga tegishli emas."}, status=404)

        if house.status != 'deactive':
            return Response({
                "detail": "Faqat rad etilgan e’londan keyin qayta yuborish mumkin.",
                "current_status": house.status
            }, status=400)

        house.status = 'pending'
        house.is_active = False
        house.save()

        return Response({
            "detail": "E’lon qayta adminga yuborildi. Tasdiqlanishi kutilmoqda.",
            "status_message": "Tasdiqlanmagan",
            "is_active_status": False
        }, status=status.HTTP_200_OK)


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        house_id = instance.id  # oldindan ID ni olish
        self.perform_destroy(instance)
        return Response(
            {"message": f"House #{house_id} deleted successfully."},
            status=status.HTTP_200_OK
        )


class HouseImageDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        try:
            image = House_image.objects.get(id=id)
        except House_image.DoesNotExist:
            return Response({"error": "Rasm topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        # Foydalanuvchi ruxsatini tekshirish
        if image.house.owner != request.user:
            return Response({"detail": "Siz faqat o‘z rasmingizni o‘chira olasiz."}, status=status.HTTP_403_FORBIDDEN)

        # O‘chirish
        image.delete()
        return Response({"message": "Rasm muvaffaqiyatli o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)


class RegionListAPIView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class RegionDetailWithDistrictsAPIView(APIView):
    def get(self, request, region_id):
        region = get_object_or_404(Region, id=region_id)
        serializer = RegionSerializer(region)
        return Response(serializer.data)


class ToggleSaveHouseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            house = House.objects.get(pk=pk)
        except House.DoesNotExist:
            return Response({"error": "Uy topilmadi"}, status=404)

        user = request.user
        if house.saved_by.filter(id=user.id).exists():
            house.saved_by.remove(user)
            return Response({"saved": False, "message": "Saqlanganlardan chiqarildi"})
        else:
            house.saved_by.add(user)
            return Response({"saved": True, "message": "Uy saqlandi"})


class SavedHouseListAPIView(generics.ListAPIView):
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.saved_houses.filter(is_active=True, status='active')
