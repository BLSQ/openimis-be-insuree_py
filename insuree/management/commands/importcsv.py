import csv
import os

from core import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from location.models import Location

from insuree.models import Gender
from insuree.test_helpers import create_test_insuree, create_test_photo


def replace_dict_key(dictionary: dict, old_key: str, new_key: str):
    dictionary[new_key] = dictionary[old_key]
    dictionary.pop(old_key)


def generate_location_filters(lga_name, district_name, settlement_name):
    return Q(validity_to__isnull=True) \
           & Q(name=settlement_name) \
           & Q(type="V") \
           & Q(parent__name=district_name) \
           & Q(parent__validity_to__isnull=True) \
           & Q(parent__type="W") \
           & Q(parent__parent__name=lga_name) \
           & Q(parent__parent__validity_to__isnull=True) \
           & Q(parent__parent__type="D")


GENDERS = {
    "FEMALE": Gender.objects.get(code='F'),
    "MALE": Gender.objects.get(code='M'),
}


class Command(BaseCommand):
    help = "This command will import Insurees from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_location",
                            nargs=1,
                            type=str,
                            help="Absolute path to the CSV file")

    def handle(self, *args, **options):
        file_location = options["csv_location"][0]
        if not os.path.isfile(file_location):
            print(f"Error - {file_location} is not a correct file path.")
        else:
            with open(file_location, mode='r', encoding='utf-8-sig') as csv_file:

                total_rows = 0
                photo_root = os.environ.get("PHOTO_ROOT_PATH", "/data/photos")

                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:

                    total_rows += 1
                    print(f"{total_rows} - starting Insuree {row['nin']}")

                    json_ext = {}
                    validity_from = datetime.datetime.now()

                    # Making a copy of raw data to store in json + cleaning fields
                    for key in row:
                        row[key] = row[key].strip()
                        json_ext[key] = row[key]
                    row["json_ext"] = json_ext

                    # Changing key names if data is ok as is
                    replace_dict_key(row, "nin", "chf_id")
                    replace_dict_key(row, "family_name", "last_name")
                    replace_dict_key(row, "given_name", "other_names")
                    replace_dict_key(row, "date_of_birth", "dob")
                    replace_dict_key(row, "mobile_number", "phone")

                    # Adding new keys and editing data
                    row["head"] = True
                    row["validity_from"] = validity_from
                    row["dob"] = datetime.datetime.strptime(row["dob"], '%d/%m/%Y').strftime('%Y-%m-%d')
                    row["place_of_birth"] = row["pob_health_facility"] if row["pob_health_facility"] else row["pob_city"]
                    row["gender"] = GENDERS.get(row["sex"], Gender.objects.get(code='O'))
                    row["father_name"] = f"{row['father_name']} {row['father_lastname']}"
                    row["mother_name"] = f"{row['mother_name']} {row['mother_lastname']}"
                    row["is_local"] = row["nationality"] == row["pob_country"]

                    # Removing fields that are not directly stored
                    row.pop("id")
                    row.pop("nationality")
                    row.pop("sex")
                    row.pop("father_lastname")
                    row.pop("mother_lastname")
                    row.pop("contact_person")
                    row.pop("pob_place_type")
                    row.pop("pob_country")
                    row.pop("pob_lga")
                    row.pop("pob_district")
                    row.pop("pob_city")
                    row.pop("pob_health_facility")
                    row.pop("content_type")
                    row.pop("document_type")
                    photo_filename = row.pop("filename")

                    # Preparing the Family data
                    family_props = {
                        "validity_from": validity_from
                    }

                    # Filtering the person's residence location
                    if row["res_city"] and row["res_district"] and row["res_lga"]:
                        location_filters = generate_location_filters(row["res_lga"],
                                                                     row["res_district"],
                                                                     row["res_city"])
                    else:
                        # No information on the person's residence -> registration place
                        location_filters = generate_location_filters(row["por_lga"],
                                                                     row["por_district"],
                                                                     row["por_city"])

                    location = Location.objects.filter(location_filters).first()
                    if location:
                        family_props["location"] = location
                    else:
                        if row["res_city"] and row["res_district"] and row["res_lga"]:
                            location_string = f"Residence={row['res_lga']} - {row['res_district']} - {row['res_city']}"
                        else:
                            location_string = f"Registration={row['por_lga']} - {row['por_district']} - {row['por_city']}"

                    # Removing location fields
                    row.pop("res_country")
                    row.pop("res_lga")
                    row.pop("res_district")
                    row.pop("res_city")
                    row.pop("por_lga")
                    row.pop("por_district")
                    row.pop("por_city")

                    # Inserting data into the DB
                    # check NIN validity + existing NIN?
                    insuree = create_test_insuree(with_family=True, is_head=True, custom_props=row, family_custom_props=family_props)
                    photo_props = {
                        "photo": "",
                        "chf_id": insuree.chf_id,
                        "folder": photo_root,
                        "filename": photo_filename,
                        "validity_from": validity_from,
                    }
                    photo = create_test_photo(insuree_id=insuree.id, officer_id=-1, custom_props=photo_props)
                    insuree.photo = photo
                    insuree.save()

                    # Printing result
                    if location:
                        print(f"{total_rows} - insuree {row['chf_id']} created with location")
                    else:
                        print(f"{total_rows} - insuree {row['chf_id']} without any location. Location invalid: [{location_string}]")
                    print("---------")


                print(f"Import finished: {total_rows} insurees created")
