from django.contrib import admin

from restaurant_ratings.inspections.models import Inspection
from . import models


class InspectionInlines(admin.TabularInline):
    extra = 0
    model = Inspection


@admin.register(models.Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [InspectionInlines]