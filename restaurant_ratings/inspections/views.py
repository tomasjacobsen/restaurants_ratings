from django.conf import settings
from django.utils import timezone
from django.db.models import Q, QuerySet, Max, Min

from django.views.generic import TemplateView
from dateutil.relativedelta import relativedelta
import datetime
from . import models

class Frontpage(TemplateView):
    template_name = "inspections/frontpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        to_date: datetime.datetime = timezone.now()
        from_date: datetime.datetime = to_date - relativedelta(**settings.MATTILSYNET_OLDEST_DATE)

        best_rating = models.Inspection.objects.filter(date__gte=from_date).aggregate(Min('total_rating'))['total_rating__min']
        worst_rating = models.Inspection.objects.filter(date__gte=from_date).aggregate(Max('total_rating'))['total_rating__max']

        best_inspections_qs = models.Inspection.objects.filter(date__gte=from_date, total_rating__lte=best_rating).select_related('restaurant').order_by('-total_rating', '-date')[:10]
        worst_inspections_qs = models.Inspection.objects.filter(date__gte=from_date, total_rating__gte=worst_rating).select_related('restaurant').order_by('total_rating', '-date')[:10]


        context['best_inspections'] = best_inspections_qs
        context['worst_inspections'] = worst_inspections_qs

        return context