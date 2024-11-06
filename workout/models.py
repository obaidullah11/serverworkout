from django.db import models
from train.models import Exercise
from django.core.exceptions import ValidationError

class Folder(models.Model):
    name = models.CharField(max_length=100)  # Field to store the folder name
    created_at = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255)
      # Automatically set the timestamp when created

    def __str__(self):
        return self.name


class Workout(models.Model):
    device_id = models.CharField(max_length=255,null=True,blank=True)  # Use device_id instead of User
    name = models.CharField(max_length=255)  # Workout name (e.g., 'Leg Day', 'Push Day')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=1000,null=True,blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='workouts')  # Link to Folder model
    def __str__(self):
        return f'{self.name} - {self.device_id}'


class workoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="perform_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="perform_exercises")  # Link to Exercise
    order = models.PositiveIntegerField(default=0)  # Order of the exercise in the workout

    def __str__(self):
        return f'{self.exercise.name} in {self.workout.name}'

    def clean(self):
        """Ensure that exercise order is not negative."""
        if self.order < 0:
            raise ValidationError("Order must be a non-negative value.")

class Set(models.Model):
    workoutExercise = models.ForeignKey(workoutExercise, on_delete=models.CASCADE, related_name="sets")
    set_number = models.PositiveIntegerField()  # Set number (e.g., Set 1, Set 2)
    kg = models.DecimalField(max_digits=5, decimal_places=2)  # Preset weight in kg
    reps = models.PositiveIntegerField()  # Preset number of repetitions

    def __str__(self):
        return f'{self.workoutExercise.exercise.name} - Set {self.set_number}: {self.kg}kg x {self.reps}'


# Track user performance for each workout session
class WorkoutSession(models.Model):
    device_id = models.CharField(max_length=255,null=True,blank=True)  # Use device_id instead of User
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="workout_sessions")
    date = models.DateTimeField(auto_now_add=True)
     
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'{self.device_id} - {self.workout.name} on {self.date}'

# Track actual performance for each set in a workout session
class SetPerformance(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="set_performances")
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    actual_kg = models.DecimalField(max_digits=5, decimal_places=2)  # Actual weight lifted
    actual_reps = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # Actual reps performed

    def __str__(self):
        return f'{self.session.workout.name} - Set {self.set.set_number}: {self.actual_kg}kg x {self.actual_reps} reps'

    def clean(self):
        """Ensure actual values are logical."""
        if self.actual_kg < 0:
            raise ValidationError("Weight must be a positive value.")
        if self.actual_reps < 0:
            raise ValidationError("Reps must be a positive value.")
        if self.actual_kg > self.set.kg:
            raise ValidationError("Actual weight cannot exceed the set weight.")
        
# models.py


class WorkoutHistory(models.Model):
    device_id = models.CharField(max_length=255)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE)
    highest_weight = models.DecimalField(max_digits=5, decimal_places=2)  # Track the highest weight lifted
    best_performance_set = models.ForeignKey(SetPerformance, on_delete=models.CASCADE)  # Reference to best performance set
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when created
    workout_time = models.DurationField(null=True, blank=True)
    def __str__(self):
        return f"Workout History for {self.workout.name} - {self.device_id} on {self.created_at}"

class SetHistory(models.Model):
    workout_history = models.ForeignKey(WorkoutHistory, on_delete=models.CASCADE, related_name='set_histories')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)  # Link to the exercise
    set_number = models.PositiveIntegerField()  # The set number
    actual_kg = models.DecimalField(max_digits=5, decimal_places=2)  # Actual weight lifted
    actual_reps = models.PositiveIntegerField()  # Actual reps performed
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when created
    rm = models.FloatField(null=True, blank=True)
    pr = models.IntegerField(default=0) 
    def __str__(self):
        return f"Set History: {self.exercise.name} - Set {self.set_number} on {self.created_at}"
from django.db import models

class CoreMeasurement(models.Model):
    device_id = models.CharField(max_length=100)  # Adjust max_length as needed
    waist_circumference = models.FloatField()
    hip_circumference = models.FloatField()
    chest_circumference = models.FloatField()

    def __str__(self):
        return f"Core Measurement for Device {self.device_id}"


class BodyPartMeasurement(models.Model):
    device_id = models.CharField(max_length=100)  # Should correspond with CoreMeasurement
    arm_circumference = models.FloatField()
    thigh_circumference = models.FloatField()
    calf_circumference = models.FloatField()

    def __str__(self):
        return f"Body Part Measurement for Device {self.device_id}"
