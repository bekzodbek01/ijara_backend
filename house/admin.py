from django.contrib import admin
from .models import House, House_image


class HouseImageInline(admin.TabularInline):  # yoki StackedInline
    model = House_image
    extra = 1  # Qo‘shimcha 1 ta bo‘sh forma ko‘rsatadi


class HouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'address', 'room_count', 'views_count']
    search_fields = ['address', 'description']
    inlines = [HouseImageInline]  # House_image modelini Inline tarzda qo‘shish


admin.site.register(House, HouseAdmin)
