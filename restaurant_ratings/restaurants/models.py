from django.db import models


class Restaurant(models.Model):
    organization_number = models.CharField(max_length=9)
    name = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=4)
    postal_address = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name
