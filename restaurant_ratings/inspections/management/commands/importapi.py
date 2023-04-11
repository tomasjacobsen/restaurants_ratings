from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand

from typing import Dict, List
from dateutil.relativedelta import relativedelta
import requests
import datetime
import time

from restaurant_ratings.restaurants.models import Restaurant
from restaurant_ratings.inspections import models

MIN_TIME_BETWEEN_REQUESTS = 0.1

class Inspection:

    def __init__(self, data):
        self.tilsynsbesoektype = data.get('tilsynsbesoektype')
        self.poststed = data.get('poststed')
        self.sakref = data.get('sakref')
        self.tilsynsobjektid = data.get('tilsynsobjektid')
        self.orgnummer = data.get('orgnummer')
        self.postnr = data.get('postnr')
        self.dato = data.get('dato')
        self.navn = data.get('navn')
        self.tema1_no = data.get('tema1_no')
        self.tema3_nn = data.get('tema3_nn')
        self.tema1_nn = data.get('tema1_nn')
        self.tema3_no = data.get('tema3_no')
        self.tilsynid = data.get('tilsynid')
        self.adrlinje1 = data.get('adrlinje1')
        self.karakter1 = data.get('karakter1')
        self.adrlinje2 = data.get('adrlinje2')
        self.karakter2 = data.get('karakter2')
        self.karakter3 = data.get('karakter3')
        self.karakter4 = data.get('karakter4')
        self.total_karakter = data.get('total_karakter')
        self.tema4_no = data.get('tema4_no')
        self.tema4_nn = data.get('tema4_nn')
        self.tema2_no = data.get('tema2_no')
        self.status = data.get('status')
        self.tema2_nn = data.get('tema2_nn')

    def get_rating_by_theme(self) -> List[Dict[int, str]]:
        theme_list = []
        for i in range(1,4):
            theme = getattr(self, f"tema{i}_no")
            rating = getattr(self, f"karakter{i}")
            if theme and rating:
                theme_list.append({
                    "theme": i,
                    "rating": rating
                })
        return theme_list


def request_api_data(url:str, params:object) -> List[Inspection]:
    
    entries = []
    page = 1

    while True:
        params["page"] = page
        try:
            response = requests.get(url, params=params, timeout=5, verify=True)
            response.raise_for_status()

            data = response.json()
            
            if not data["entries"]:
                break

            for entry_data in data["entries"]:
                entry = Inspection(data=entry_data)
                entries.append(entry)
            if data["page"] == data["pages"]:
                break
            page += 1
        


        except requests.exceptions.HTTPError as errh:
            raise(errh.args[0])
        except requests.exceptions.ReadTimeout as errrt:
            raise("Time out")
        except requests.exceptions.ConnectionError as conerr:
            raise("Connection error")
        except requests.exceptions.RequestException as errex:
            raise("Exception request")



    return entries



class Command(BaseCommand):
    help = "Imports ratings done by Mattilsynet"

    def handle(self, *args, **options):
        """
        Function to import data from api, 
        using env variable not to import entries older than relative date
        """
        number_of_entries = 0
        rate_limit_start = time.monotonic()
        to_date: datetime.datetime = timezone.now()
        from_date: datetime.datetime = to_date - relativedelta(**settings.MATTILSYNET_OLDEST_DATE)


        self.stdout.write(
            self.style.SUCCESS('Starting import of inspections from %s to %s' % (from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')))
        )

        # Since the external api does not allow query based on dateperiod,
        # we need to loop over every day in the period, to find entries
        
        current_date: datetime.datetime = from_date

        while current_date <= to_date:
            
            #Get entries for this day
            params: object = {'dato': current_date.strftime('%d%m%Y')} # 01022023
            entries: list(Inspection) = request_api_data(url=settings.MATTILSYNET_BASE_URL, params=params)

            self.stdout.write(
                self.style.SUCCESS('Importing %s inspections from %s' % (len(entries), current_date.strftime('%Y-%m-%d')))
            )

            for entry in entries:
                
                # Get or create the restaurant
                restaurant, _ = Restaurant.objects.get_or_create(
                    organization_number=entry.orgnummer,
                        defaults={
                            'name': entry.navn,
                            'postal_code': entry.postnr,
                            'postal_address': entry.poststed,
                            'address': f"{entry.adrlinje1}\n{entry.adrlinje2}" if entry.adrlinje2 else f"{entry.adrlinje1}"
                        }
                    )

                # Get or create the inspection
                inspection, inspection_created = models.Inspection.objects.get_or_create(
                    identifier=entry.tilsynsobjektid,
                    restaurant=restaurant,
                        defaults={
                            'is_pending': bool(int(entry.status)),
                            'date': datetime.datetime.strptime(entry.dato, '%d%m%Y').date(),
                            'total_rating': int(entry.total_karakter)
                        }
                )

                if inspection_created:
                    # New inspection, save extra fields
                    theme_ratings = entry.get_rating_by_theme()

                    for theme_rating in theme_ratings:
                        models.InspectionTheme.objects.create(inspection=inspection, theme=theme_rating['theme'], rating=theme_rating['rating'])
                
                number_of_entries += 1

            # Make sure the request does not exceed the rate-limit
            time_since_last_request = time.monotonic() - rate_limit_start
            if time_since_last_request < MIN_TIME_BETWEEN_REQUESTS:
                time.sleep(MIN_TIME_BETWEEN_REQUESTS - time_since_last_request)
            rate_limit_start = time.monotonic()

            current_date += relativedelta(days=1) 

        self.stdout.write(
            self.style.SUCCESS('Successfully imported %s inspections' % number_of_entries)
        )

