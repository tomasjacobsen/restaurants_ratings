from django.db import models


class Rating(models.IntegerChoices):
    BEST = 0, "Ingen brudd på regelverket funnet. Stort smil."
    GOOD = 1, "Mindre brudd på regelverket som ikke krever oppfølging. Stort smil."
    NOT_GOOD = 2, "Brudd på regelverket som krever oppfølging. Strekmunn."
    BAD = 3, "Alvorlig brudd på regelverket. Sur munn."


class Inspection(models.Model):
    identifier = models.CharField(max_length=255)
    restaurant = models.ForeignKey('restaurants.Restaurant', related_name='inspections', on_delete=models.CASCADE)
    is_pending = models.BooleanField(default=False)
    date = models.DateField()
    total_rating = models.IntegerField(choices=Rating.choices)


    def __str__(self):
        return f"{self.restaurant}: {self.total_rating} ({self.date})"


class InspectionTheme(models.Model):
    
    class Theme(models.IntegerChoices):
        ROUTINES_AND_MANAGEMENT = 1, "Rutiner og ledelse"
        PREMISES_AND_EQUIPMENT = 2, "Lokaler og utstyr"
        FOOD_HANDLING_AND_PREPARATION = 3, "Mat-håndtering og tilberedning"
        MARKING_AND_TRACEABILITY = 4, "Merking og sporbarhet"


    inspection = models.ForeignKey('inspections.Inspection', related_name='inspection_themes', on_delete=models.CASCADE)
    theme = models.IntegerField(choices=Theme.choices)
    rating = models.IntegerField(choices=Rating.choices)

    def __str__(self):
        return f"{self.get_theme_display()}: {self.rating}"