from django.db import models
from users.models import AbstractUser

class House(models.Model):
    owner = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, related_name='houses')
    image = models.ImageField(upload_to='houses/')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    room_count = models.IntegerField()
    description = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # ko‘rsatilgan bo‘lsa
    views_count = models.PositiveIntegerField(default=0)
    contacts_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.district} - {self.price}$"
