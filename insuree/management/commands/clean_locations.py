import logging

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from ecrvs.models import HeraLocationIDsMapping
from ecrvs.services import get_hera_location_mapping_by_hera_code
from insuree.models import Insuree
from location.models import Location

HERA_UNKNOWN_VILLAGE_ID = 5857
FIRST_HERA_LOCATION_ID = 4881

logger = logging.getLogger(__name__)


def get_hera_location_mappings():
    dict_mappings = {}
    mappings = HeraLocationIDsMapping.objects.filter(is_instance_deleted=False, location_type='V').all()
    for mapping in mappings:
        dict_mappings[mapping.hera_code] = mapping.openimis_location_id
    return dict_mappings


class Command(BaseCommand):
    help = "This command will clean old locations set to families in order to use the ones that are coming from Hera"

    def handle(self, *args, **options):
        logger.info("*** CLEANING LOCATIONS IN FAMILIES ***")
        unknown_village = Location.objects.filter(id=HERA_UNKNOWN_VILLAGE_ID).first()

        total = 0
        skipped = 0
        error_no_mapping = 0
        updated = 0

        insurees = (Insuree.objects.filter(validity_to__isnull=True)
                                   .prefetch_related("family")
                                   .order_by("id"))
        # for insuree in insurees.iterator(chunk_size=1000):

        hera_location_mapping_dict = get_hera_location_mappings()

        # https://nextlinklabs.com/resources/insights/django-big-data-iteration
        paginator = Paginator(insurees, 1000)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)

            for insuree in page.object_list:
                total += 1
                logger.info(f"\tprocessing {insuree.chf_id}")

                family = insuree.family
                if family.location_id >= FIRST_HERA_LOCATION_ID:
                    logger.info(f"\t\talready in the new location pyramid, nothing to do")
                    skipped += 1
                    continue

                json_ext = insuree.json_ext
                if not json_ext:
                    logger.warning(f"\t\tno json ext data -> sending to unknown village")
                    family.location = unknown_village
                    family.save()
                    skipped += 1
                    continue

                # old insurees that were inserted by xlsx imports in 2023
                # and that were not updated by Hera in April/May 2024 don't have the proper field value
                # so we can skip them or place them in village unknown
                if "registrationVillage" not in json_ext:
                    logger.warning(f"\t\tno registrationVillage in json ext data -> sending to unknown village")
                    family.location = unknown_village
                    family.save()
                    skipped += 1
                    continue

                # get village from payload
                village_hera_code = json_ext["registrationVillage"]
                if "residentialVillage" in json_ext and json_ext["residentialVillage"]:
                    village_hera_code = json_ext["residentialVillage"]

                openimis_village_id = hera_location_mapping_dict.get(village_hera_code, None)

                if not openimis_village_id:
                    logger.error(f"\t\tno village mapping for {village_hera_code} -> sending to unknown village")
                    family.location = unknown_village
                    family.save()
                    error_no_mapping += 1
                    continue

                logger.info(f"\t\tvillage found ({village_hera_code}) -> sending to village ID {openimis_village_id}")
                family.location_id = openimis_village_id
                family.save()
                updated += 1

        logger.info("**************************************")
        logger.info(f"Total insurees: {total}")
        logger.info(f"- updated: {updated}")
        logger.info(f"- skipped: {skipped}")
        logger.info(f"- error no mapping: {error_no_mapping}")
