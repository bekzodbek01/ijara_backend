from django.db import models
from users.models import AbstractUser


class House(models.Model):
    owner = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, related_name='houses')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    room_count = models.IntegerField()
    description = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # ko‘rsatilgan bo‘lsa
    views_count = models.PositiveIntegerField(default=0)
    contacts_count = models.PositiveIntegerField(default=0)
    # STATUS_CHOICES = [
    #     ('pending', 'Kutilmoqda'),
    #     ('active', 'Faol'),
    #     ('deactive', 'NoFaol'),
    # ]
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.district} - {self.price}$"


class House_image(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_image', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.house.address}"
