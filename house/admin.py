from django.contrib import admin, messages
from .models import House, House_image, District, Region


class HouseImageInline(admin.TabularInline):  # yoki StackedInline
    model = House_image
    extra = 1  # Qo‘shimcha 1 ta bo‘sh forma ko‘rsatadi


class HouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'region', 'status', 'is_active', 'room_count', 'views_count']
    search_fields = ['region', 'description']
    inlines = [HouseImageInline]  # House_image modelini Inline tarzda qo‘shish
    ctions = ['approve_houses', 'reject_houses']

    def get_readonly_fields(self, request, obj=None):
        # Faqat superuser statusni o‘zgartira oladi
        if not request.user.is_superuser:
            return ['status']
        return []

    @admin.action(description='✅ E’lonni tasdiqlash (active)')
    def approve_houses(self, request, queryset):
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f"{updated} ta e’lon faol holatga o‘tkazildi.", messages.SUCCESS)

    @admin.action(description='🚫 E’lonni rad etish (deactive)')
    def reject_houses(self, request, queryset):
        updated = queryset.update(status='deactive', is_active=False)
        self.message_user(request, f"{updated} ta e’lon rad etildi.", messages.WARNING)


admin.site.register(House, HouseAdmin)
admin.site.register(District)


class DistrictInline(admin.TabularInline):  # yoki admin.StackedInline
    model = District
    extra = 1


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [DistrictInline]