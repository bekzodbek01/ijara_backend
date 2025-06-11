from django.contrib import admin

from users.models import AbstractUser, FaceComparison

admin.site.register(AbstractUser)


@admin.register(FaceComparison)
class FaceComparisonAdmin(admin.ModelAdmin):
    list_display = ('match_result', 'created_at')

