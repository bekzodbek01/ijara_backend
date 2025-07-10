from django.db import models

from config import settings
from users.models import AbstractUser
from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')

    class Meta:
        unique_together = ('name', 'region')

    def __str__(self):
        return f"{self.region.name} - {self.name}"


class House(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('active', 'Faol'),
        ('deactive', 'NoFaol'),
    ]
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_houses',
        blank=True
    )

    owner = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, related_name='houses')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    room_count = models.IntegerField()
    description = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # ko‘rsatilgan bo‘lsa
    views_count = models.PositiveIntegerField(default=0)
    contacts_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.price}$"


class House_image(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_image', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.house.title}"
