"""Models for Personal Training App"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from users.models import User
from django.db import models
from django.core.exceptions import ValidationError
from moviepy.editor import VideoFileClip
import os
from PIL import Image
class Category(models.Model):
    """Category for exercises (e.g., Strength, Cardio, Flexibility)"""
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """Exercise such as plank, squat, row"""

    name = models.CharField(max_length=40, unique=True)
    body_part = models.CharField(max_length=225,)
    instructions = models.CharField(max_length=800, blank=True)
    gif = models.FileField(upload_to='exercise_videos/', null=True, blank=True)
    exercise_image = models.FileField(upload_to='exercise_images/', null=True, blank=True)  # New field for image
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exercises', null=True, blank=True)
    device_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    equipment = models.CharField(max_length=100,  blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Compress GIF or video if gif exists
        if self.gif:
            file_size = self.gif.size / (1024 * 1024)  # Convert size to MB
            file_path = self.gif.path
            if file_size > 2:
                if file_path.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
                    self.compress_video(file_path)
                elif file_path.endswith('.gif'):
                    self.compress_gif(file_path)

        # Compress exercise image if it exists
        if self.exercise_image:
            file_size = self.exercise_image.size / (1024 * 1024)  # Convert size to MB
            file_path = self.exercise_image.path
            if file_size > 1:  # If image size is greater than 1MB, compress it
                self.compress_image(file_path)

        super().save(*args, **kwargs)

    def compress_video(self, file_path):
        """Compress video file to reduce size below 2MB."""
        clip = VideoFileClip(file_path)
        clip_resized = clip.resize(height=360)
        compressed_path = file_path.replace(".mp4", "_compressed.mp4")
        clip_resized.write_videofile(compressed_path, bitrate="500k", codec='libx264')
        os.replace(compressed_path, file_path)

    def compress_gif(self, file_path):
        """Compress GIF file to reduce size below 2MB."""
        gif = Image.open(file_path)
        gif.thumbnail((480, 480))  # Resize to reduce file size
        compressed_path = file_path.replace(".gif", "_compressed.gif")
        gif.save(compressed_path, format='GIF', optimize=True, quality=85)
        os.replace(compressed_path, file_path)

    def compress_image(self, file_path):
        """Compress image file to reduce size below 1MB."""
        image = Image.open(file_path)

        # Define a loop to reduce image quality until it meets the size limit
        quality = 85
        while os.path.getsize(file_path) > (1 * 1024 * 1024):  # Check if the file size is still larger than 1MB
            image.save(file_path, optimize=True, quality=quality)
            quality -= 5  # Decrease quality to further reduce file size

            # Break the loop if quality is too low to avoid too much degradation
            if quality < 20:
                break



