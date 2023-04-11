from django.contrib import admin
from . import models

class InspectionThemeInlines(admin.TabularInline):
    extra = 0
    model = models.InspectionTheme


@admin.register(models.Inspection)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [InspectionThemeInlines]
