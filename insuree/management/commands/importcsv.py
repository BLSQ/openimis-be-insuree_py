import csv
import json
import os.path
from django.core.management.base import BaseCommand
from insuree.test_helpers import create_test_insuree

from insuree.models import Insuree, Gender


def replace_dict_key(dictionary: dict, old_key: str, new_key: str):
    dictionary[new_key] = dictionary[old_key]
    dictionary.pop(old_key)


GENDERS = {
    "FEMALE": 'F',
    "MALE": 'M',
    # "FEMALE": Gender.objects.get(code='F'),
    # "MALE": Gender.objects.get(code='M'),
}
BIRTH_HOME = "HOME"
BIRTH_HOSPITAL = "HOSPITAL"
AVAILABLE_BIRTHS = [BIRTH_HOME, BIRTH_HOSPITAL]


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
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:

                    json_ext = {}

                    # Making a copy of raw data to store in json + cleaning
                    for key in row:
                        row[key] = row[key].strip()
                        json_ext[key] = row[key]

                    # Changing key names if data is ok as is
                    replace_dict_key(row, "national_subdivision", "LGA")
                    replace_dict_key(row, "city", "village")
                    replace_dict_key(row, "family_name", "last_name")
                    replace_dict_key(row, "given_name", "other_names")
                    replace_dict_key(row, "date_of_birth", "dob")
                    replace_dict_key(row, "mobile_number", "phone")

                    # Adding new keys and updating data
                    row["head"] = True
                    row["gender"] = GENDERS.get(row["sex"], 'O')
                    # row["gender"] = GENDERS.get(row["sex"], Gender.objects.get(code='O'))
                    row.pop("sex")
                    row["father_name"] = f"{row['father_name']} {row['father_lastname']}"
                    row.pop("father_lastname")
                    row["mother_name"] = f"{row['mother_name']} {row['mother_lastname']}"
                    row.pop("mother_lastname")
                    row["is_local"] = row["nationality"] == row["country"]
                    row.pop("nationality")

                    # Removing fields that are not directly stored
                    row.pop("contact_person")
                    row.pop("place_type")
                    row.pop("country")
                    row.pop("LGA")
                    row.pop("district")
                    row.pop("village")
                    row.pop("health_facility")

                    # NIN missing


                    print(json.dumps(row, indent=4))
                    # print(json.dumps(json_ext, indent=4))
                    print("---------")

                    # create_test_insuree(with_family=True, is_head=True, custom_props=row)

