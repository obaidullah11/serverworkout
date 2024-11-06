import json
from django.core.management.base import BaseCommand
from train.models import Category

class Command(BaseCommand):
    help = 'Load categories from a JSON file'

    def handle(self, *args, **kwargs):
        # Categories data from JSON
        categories_data = [
            "abductors",
            "abs",
            "adductors",
            "biceps",
            "calves",
            "cardiovascular system",
            "delts",
            "forearms",
            "glutes",
            "hamstrings",
            "lats",
            "levator scapulae",
            "pectorals",
            "quads",
            "serratus anterior",
            "spine",
            "traps",
            "triceps",
            "upper back"
        ]

        for category_name in categories_data:
            # Create category if it does not exist
            Category.objects.get_or_create(name=category_name)

        self.stdout.write(self.style.SUCCESS('Successfully loaded categories.'))
