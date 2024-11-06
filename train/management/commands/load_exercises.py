from django.conf import settings
from django.core.management.base import BaseCommand
from train.models import Exercise, Category
import os
import json

class Command(BaseCommand):
    help = 'Load exercises from a JSON file'

    def handle(self, *args, **kwargs):
        print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

        with open('train/management/commands/exercises.json') as json_file:
            exercises = json.load(json_file)
            for exercise in exercises:
                print(f"Processing exercise: {exercise['name']}")

                # Clean up image path and verify it exists
                image_path = exercise['exercise_image'].lstrip('/')
                full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

                print(f"Image path from JSON: {image_path}")
                print(f"Computed full image path: {full_image_path}")

                # Check if the image file exists
                if not os.path.isfile(full_image_path):
                    self.stdout.write(self.style.ERROR(f"Image not found at {full_image_path}."))
                    continue

                # Fetch or create the category instance
                category_name = exercise['category_name']  # Assuming category_name in JSON is intended to link to Category
                category, created = Category.objects.get_or_create(name=category_name)

                # Check if the exercise already exists
                exercise_name = exercise['name']
                exercise_instance, created = Exercise.objects.get_or_create(
                    name=exercise_name,
                    defaults={
                        'exercise_image': image_path,  # Assuming `exercise_image` is an ImageField or FileField in `Exercise`
                        'body_part': exercise['body_part'],
                        'instructions': exercise['instructions'],
                        'gif': exercise['gif'],
                        'category': category,  # Using the Category instance
                        'equipment': exercise['equipments'],  # Assuming `equipment` is also a field in Exercise
                    }
                )

                if created:
                    print(f"Successfully created Exercise: {exercise_name}")
                else:
                    print(f"Exercise already exists, skipping: {exercise_name}")

        self.stdout.write(self.style.SUCCESS('Successfully loaded exercises.'))
