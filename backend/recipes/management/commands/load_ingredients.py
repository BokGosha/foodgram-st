import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к JSON-файлу')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)

            for item in ingredients:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )

        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены!'))
