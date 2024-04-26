import json

from django.core.management.base import BaseCommand
from ricept.models import Ingredient


class Command(BaseCommand):
    help = "Imports JSON data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file containing data"
        )

    def handle(self, *args, **options):
        with open(options["json_file"], "r", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.create(
                    name=item["name"],
                    measurement_unit=item["measurement_unit"]
                )
        self.stdout.write(self.style.SUCCESS("Successfully imported data"))
