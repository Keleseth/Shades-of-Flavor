import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Команда для создания списка объектов из .csv файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='путь к csv файлу'
        )
        parser.add_argument(
            'model_to_load',
            type=str,
            help='модель для создания объектов.'
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        model_name = kwargs['model_to_load']

        try:
            app_label, model_name = model_name.split(".")
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            self.stdout.write(
                self.style.ERROR(f'Модель "{model_name}" не найдена.')
            )
            return

        model_fields = [
            field.name for field in Model._meta.fields if field.name != 'id'
        ]

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    data = {}
                    for element_index, value in enumerate(row):
                        if element_index < len(model_fields):
                            data[model_fields[element_index]] = value
                    obj, created = Model.objects.get_or_create(**data)
                    if created:
                        self.stdout.write(f'Объект: {data} создан')
                    else:
                        self.stdout.write(f'Объект: {data} не был создан')
        except FileNotFoundError:
            self.stdout.write(f'{csv_file} не найден.')
