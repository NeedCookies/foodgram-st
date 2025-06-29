# Стандартная библиотека
import json

# Сторонние библиотеки
from django.core.management.base import BaseCommand

# Локальные импорты
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the JSON file")

    def handle(self, *args, **options):
        file_path = options["file"]
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            Ingredient.objects.get_or_create(
                name=item["name"], measurement_unit=item["measurement_unit"]
            )

        self.stdout.write(self.style.SUCCESS("Ingredients loaded."))
