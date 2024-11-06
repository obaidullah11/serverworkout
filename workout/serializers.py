from rest_framework import serializers
from .models import CoreMeasurement, BodyPartMeasurement,Workout,SetHistory, workoutExercise, Set, WorkoutSession, SetPerformance,Folder,WorkoutHistory
from train.models import Exercise
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models import Max
from django.db import models
from train.serializers import ExerciseSerializer
from rest_framework import serializers
 

# serializers.py
from rest_framework import serializers
from .models import CoreMeasurement, BodyPartMeasurement

class CoreMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreMeasurement
        fields = ['waist_circumference', 'hip_circumference', 'chest_circumference']  # Exclude device_id

class BodyPartMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyPartMeasurement
        fields = ['arm_circumference', 'thigh_circumference', 'calf_circumference']  # Exclude device_id

class FolderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = ['id', 'name', 'device_id']  # Added device_id to the fields

    def create(self, validated_data):
        # You can customize the folder creation logic as needed
        folder, created = Folder.objects.get_or_create(
            name=validated_data['name'], device_id=validated_data['device_id']
        )
        return folder
class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = ['id', 'set_number', 'kg', 'reps']

class workoutExerciseSerializer(serializers.ModelSerializer):
    sets = SetSerializer(many=True)

    class Meta:
        model = workoutExercise
        fields = ['exercise', 'order', 'sets']






class WorkoutSerializernew(serializers.ModelSerializer):
    perform_exercises = workoutExerciseSerializer(many=True)
    folder = serializers.CharField(write_only=True)  # Expect folder name from the request

    class Meta:
        model = Workout
        fields = ['device_id', 'name', 'folder', 'perform_exercises']  # Include folder in fields

    def create(self, validated_data):
        perform_exercises_data = validated_data.pop('perform_exercises')
        folder_name = validated_data.pop('folder')  # Extract folder name from validated data

        # Get or create the folder by name
        folder, _ = Folder.objects.get_or_create(name=folder_name)

        # Create the workout and link it to the folder
        workout = Workout.objects.create(folder=folder, **validated_data)

        # Create the workout exercises and their sets
        for exercise_data in perform_exercises_data:
            sets_data = exercise_data.pop('sets')
            workout_exercise = workoutExercise.objects.create(workout=workout, **exercise_data)

            # Create sets for each workout exercise
            Set.objects.bulk_create(
                [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
            )

        # Automatically create a workout session for the workout
        WorkoutSession.objects.create(device_id=workout.device_id, workout=workout)

        return workout

    def update(self, instance, validated_data):
        perform_exercises_data = validated_data.pop('perform_exercises', None)
        folder_name = validated_data.pop('folder', None)  # Extract folder name if it is being updated

        # Update basic workout information
        instance.device_id = validated_data.get('device_id', instance.device_id)
        instance.name = validated_data.get('name', instance.name)

        if folder_name:
            # Get or create the folder by name if it is updated
            folder, _ = Folder.objects.get_or_create(name=folder_name)
            instance.folder = folder

        instance.save()

        if perform_exercises_data:
            # Update or create perform_exercises and related sets
            for exercise_data in perform_exercises_data:
                sets_data = exercise_data.pop('sets')
                workout_exercise_id = exercise_data.get('id')

                if workout_exercise_id:
                    # Update existing workout exercise
                    workout_exercise = workoutExercise.objects.get(id=workout_exercise_id, workout=instance)
                    workout_exercise.name = exercise_data.get('name', workout_exercise.name)
                    workout_exercise.save()

                    # Update the sets for the workout exercise
                    Set.objects.filter(workoutExercise=workout_exercise).delete()  # Delete old sets
                    Set.objects.bulk_create(
                        [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
                    )
                else:
                    # Create a new workout exercise and its sets
                    workout_exercise = workoutExercise.objects.create(workout=instance, **exercise_data)
                    Set.objects.bulk_create(
                        [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
                    )

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['device_id'] = instance.device_id  # Show the device_id instead of user ID

        # Retrieve the associated folder
        representation['folder'] = instance.folder.name  # Add folder name to representation

        # Retrieve the associated WorkoutSession
        workout_session = WorkoutSession.objects.filter(workout=instance).first()
        representation['session_id'] = workout_session.id if workout_session else None  # Add session ID to representation

        for exercise in representation['perform_exercises']:
            exercise_id = exercise['exercise']
            try:
                exercise_obj = Exercise.objects.get(id=exercise_id)
                # Now include all required fields from the Exercise model
                exercise['exercise'] = {
                    'id': exercise_obj.id,
                    'name': exercise_obj.name,
                    'body_part': exercise_obj.body_part,
                    'instructions': exercise_obj.instructions,
                    'gif': exercise_obj.gif.url if exercise_obj.gif else None,  # Use .url to get the URL of the file
                    'exercise_image': exercise_obj.exercise_image.url if exercise_obj.exercise_image else None,
                    'category': {
                        'id': exercise_obj.category.id if exercise_obj.category else None,
                        'name': exercise_obj.category.name if exercise_obj.category else None
                    },
                    'device_id': exercise_obj.device_id,
                }
            except Exercise.DoesNotExist:
                exercise['exercise'] = 'Unknown Exercise'

        return representation



class WorkoutSerializer(serializers.ModelSerializer):
    perform_exercises = workoutExerciseSerializer(many=True)
    folder = serializers.CharField(write_only=True)  # Expect folder name from the request

    class Meta:
        model = Workout
        fields = ['device_id', 'name', 'folder', 'notes', 'perform_exercises']

    def create(self, validated_data):
        perform_exercises_data = validated_data.pop('perform_exercises', [])
        folder_name = validated_data.pop('folder', None)

        # Debugging prints
        print(f"Creating Workout with validated_data: {validated_data}")
        print(f"Folder name received: {folder_name}")
        print(f"Perform exercises data: {perform_exercises_data}")

        # Create or get the folder instance
        folder, _ = Folder.objects.get_or_create(name=folder_name)
        print(f"Folder created or retrieved: {folder.name}")

        # Create the Workout instance
        workout = Workout.objects.create(folder=folder, **validated_data)
        print(f"Workout created: {workout.name} (ID: {workout.id})")

        # Create a new WorkoutSession associated with this workout
        workout_session = WorkoutSession.objects.create(workout=workout, device_id=validated_data['device_id'])
        print(f"WorkoutSession created: {workout_session.id} for Workout ID: {workout.id}")

        # Create workout exercises and their sets
        for exercise_data in perform_exercises_data:
            sets_data = exercise_data.pop('sets', [])
            workout_exercise = workoutExercise.objects.create(workout=workout, **exercise_data)
            print(f"WorkoutExercise created: {workout_exercise.id} for workout {workout.name}")

            # Create sets for each workout exercise
            created_sets = Set.objects.bulk_create(
                [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
            )
            print(f"Created sets: {[set.id for set in created_sets]} for workout exercise {workout_exercise.id}")

        return workout

    def update(self, instance, validated_data):
        perform_exercises_data = validated_data.pop('perform_exercises', None)
        folder_name = validated_data.pop('folder', None)

        # Debugging prints
        print(f"Updating Workout ID: {instance.id} with validated_data: {validated_data}")
        print(f"Folder name received for update: {folder_name}")

        # Update workout details
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        print(f"Updated Workout: {instance.name}")

        # Update folder if provided
        if folder_name:
            folder, _ = Folder.objects.get_or_create(name=folder_name)
            instance.folder = folder
            instance.save()
            print(f"Folder updated to: {folder.name}")

        if perform_exercises_data:
            # Delete existing workout exercises and sets
            workoutExercise.objects.filter(workout=instance).delete()
            print(f"Deleted existing workout exercises for Workout ID: {instance.id}")

            # Recreate workout exercises and their sets
            for exercise_data in perform_exercises_data:
                sets_data = exercise_data.pop('sets')
                workout_exercise = workoutExercise.objects.create(workout=instance, **exercise_data)
                print(f"WorkoutExercise created: {workout_exercise.id} for updated workout {instance.name}")

                # Create sets for each workout exercise
                created_sets = Set.objects.bulk_create(
                    [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
                )
                print(f"Created sets: {[set.id for set in created_sets]} for updated workout exercise {workout_exercise.id}")

        # Check if a new session needs to be created
        workout_session = WorkoutSession.objects.create(workout=instance, device_id=instance.device_id)
        print(f"New WorkoutSession created: {workout_session.id} for updated Workout ID: {instance.id}")

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['device_id'] = instance.device_id  # Show the device_id instead of user ID

        # Retrieve the associated folder
        representation['folder'] = instance.folder.name

        # Retrieve the associated WorkoutSession
        workout_session = WorkoutSession.objects.filter(workout=instance).first()
        representation['session_id'] = workout_session.id if workout_session else None

        # Include workout name and date/time of session
        representation['workout_name'] = instance.name


        # Calculate total weight from performances



        # Add exercise details to the representation
        exercise_details = []
        for exercise in representation['perform_exercises']:
            exercise_id = exercise['exercise']
            try:
                exercise_obj = Exercise.objects.get(id=exercise_id)
                exercise['exercise'] = exercise_obj.name
                exercise_details.append({
                    'exercise_name': exercise_obj.name,
                    'sets': exercise.get('sets', []),
                })
            except Exercise.DoesNotExist:
                exercise['exercise'] = 'Unknown Exercise'

        representation['exercise_details'] = exercise_details

        return representation

# class WorkoutSerializer(serializers.ModelSerializer):
#     perform_exercises = workoutExerciseSerializer(many=True)
#     folder = serializers.CharField(write_only=True)  # Expect folder name from the request

#     class Meta:
#         model = Workout
#         fields = ['device_id', 'name', 'folder', 'notes', 'perform_exercises']

#     def create(self, validated_data):
#         perform_exercises_data = validated_data.pop('perform_exercises', [])
#         folder_name = validated_data.pop('folder', None)

#         # Debugging prints
#         print(f"Creating Workout with validated_data: {validated_data}")
#         print(f"Folder name received: {folder_name}")
#         print(f"Perform exercises data: {perform_exercises_data}")

#         # Create or get the folder instance
#         folder, _ = Folder.objects.get_or_create(name=folder_name)
#         print(f"Folder created or retrieved: {folder.name}")

#         # Create the Workout instance
#         workout = Workout.objects.create(folder=folder, **validated_data)
#         print(f"Workout created: {workout.name} (ID: {workout.id})")

#         # Create a new WorkoutSession associated with this workout
#         workout_session = WorkoutSession.objects.create(workout=workout, device_id=validated_data['device_id'])
#         print(f"WorkoutSession created: {workout_session.id} for Workout ID: {workout.id}")

#         # Create workout exercises and their sets
#         for exercise_data in perform_exercises_data:
#             sets_data = exercise_data.pop('sets', [])
#             workout_exercise = workoutExercise.objects.create(workout=workout, **exercise_data)
#             print(f"WorkoutExercise created: {workout_exercise.id} for workout {workout.name}")

#             # Create sets for each workout exercise
#             created_sets = Set.objects.bulk_create(
#                 [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
#             )
#             print(f"Created sets: {[set.id for set in created_sets]} for workout exercise {workout_exercise.id}")

#         return workout

#     def update(self, instance, validated_data):
#         perform_exercises_data = validated_data.pop('perform_exercises', None)
#         folder_name = validated_data.pop('folder', None)

#         # Debugging prints
#         print(f"Updating Workout ID: {instance.id} with validated_data: {validated_data}")
#         print(f"Folder name received for update: {folder_name}")

#         # Update workout details
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         print(f"Updated Workout: {instance.name}")

#         # Update folder if provided
#         if folder_name:
#             folder, _ = Folder.objects.get_or_create(name=folder_name)
#             instance.folder = folder
#             instance.save()
#             print(f"Folder updated to: {folder.name}")

#         if perform_exercises_data:
#             # Delete existing workout exercises and sets
#             workoutExercise.objects.filter(workout=instance).delete()
#             print(f"Deleted existing workout exercises for Workout ID: {instance.id}")

#             # Recreate workout exercises and their sets
#             for exercise_data in perform_exercises_data:
#                 sets_data = exercise_data.pop('sets')
#                 workout_exercise = workoutExercise.objects.create(workout=instance, **exercise_data)
#                 print(f"WorkoutExercise created: {workout_exercise.id} for updated workout {instance.name}")

#                 # Create sets for each workout exercise
#                 created_sets = Set.objects.bulk_create(
#                     [Set(workoutExercise=workout_exercise, **set_data) for set_data in sets_data]
#                 )
#                 print(f"Created sets: {[set.id for set in created_sets]} for updated workout exercise {workout_exercise.id}")

#         # Check if a new session needs to be created
#         # This can be adjusted based on your logic (e.g., creating a session only if the workout is completed)
#         workout_session = WorkoutSession.objects.create(workout=instance, device_id=instance.device_id)
#         print(f"New WorkoutSession created: {workout_session.id} for updated Workout ID: {instance.id}")

#         return instance

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['device_id'] = instance.device_id  # Show the device_id instead of user ID

#         # Retrieve the associated folder
#         representation['folder'] = instance.folder.name

#         # Retrieve the associated WorkoutSession
#         workout_session = WorkoutSession.objects.filter(workout=instance).first()
#         representation['session_id'] = workout_session.id if workout_session else None

#         for exercise in representation['perform_exercises']:
#             exercise_id = exercise['exercise']
#             try:
#                 exercise_obj = Exercise.objects.get(id=exercise_id)
#                 exercise['exercise'] = exercise_obj.name
#             except Exercise.DoesNotExist:
#                 exercise['exercise'] = 'Unknown Exercise'

#         return representation



class SetPerformanceSerializer(serializers.ModelSerializer):
    set = serializers.PrimaryKeyRelatedField(queryset=Set.objects.all())

    class Meta:
        model = SetPerformance
        fields = ['set', 'actual_kg', 'actual_reps']

class SetPerformanceSerializerNew(serializers.ModelSerializer):
    exercise = serializers.SerializerMethodField()

    class Meta:
        model = SetPerformance
        fields = ['id', 'actual_kg', 'actual_reps', 'exercise']

    def get_exercise(self, obj):
        return ExerciseSerializer(obj.set.workoutExercise.exercise).data

class UpdateProgressSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    performances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.FloatField()  # Ensure actual_kg and actual_reps are validated as floats
        )
    )

    def validate(self, attrs):
        session_id = attrs.get('session_id')
        performances = attrs.get('performances')

        # Validate the session ID
        if not WorkoutSession.objects.filter(id=session_id).exists():
            raise serializers.ValidationError(f"Session ID {session_id} does not exist.")

        # Validate each performance's set ID
        for performance in performances:
            set_id = performance['set']  # Access set ID

            # Convert to integer if it's a float
            if isinstance(set_id, float):
                set_id = int(set_id)

            if not isinstance(set_id, int) or not Set.objects.filter(id=set_id).exists():
                raise serializers.ValidationError(f"Set ID {set_id} does not exist.")

        return attrs

class FolderSerializernew(serializers.ModelSerializer):
    workouts = WorkoutSerializer(many=True, read_only=True)  # Nested serializer to include workouts

    class Meta:
        model = Folder
        fields = ['id', 'name', 'created_at', 'device_id', 'workouts']  # Include workouts in the fields


class WorkoutHistorySerializer(serializers.ModelSerializer):
    set_history_data = serializers.SerializerMethodField()
    workout_name = serializers.CharField(source='workout.name', read_only=True)
    maxweight = serializers.SerializerMethodField()
    PRs = serializers.SerializerMethodField()  # For progress overload
    workout_time = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutHistory
        fields = ['id','device_id', 'workout_name', 'highest_weight', 'set_history_data', 'created_at', 'maxweight', 'PRs', 'workout_time']

    def get_set_history_data(self, obj):
        set_histories = SetHistory.objects.filter(workout_history=obj)
        return [{
            'exercise_name': set_history.exercise.name,
            'set_number': set_history.set_number,
            'actual_kg': set_history.actual_kg,
            'actual_reps': set_history.actual_reps,
            'rm': set_history.rm,  # Include RM value
             # Include PR flag (1 or 0)
        } for set_history in set_histories]

    def get_maxweight(self, obj):
        total_weight = SetPerformance.objects.filter(session=obj.session).aggregate(
            total_kg=Sum('actual_kg')
        )['total_kg'] or 0
        return total_weight

    def get_PRs(self, obj):
    # Initialize weight_difference to 0
        weight_difference = 0

        # Fetch the set history records associated with the workout history
        set_histories = SetHistory.objects.filter(workout_history=obj)

        # Iterate through each set history
        for set_history in set_histories:
            # Access the related exercise directly
            exercise = set_history.exercise
            current_kg = set_history.actual_kg

            # Fetch previous performances for the same exercise, excluding the current session
            previous_performances = SetHistory.objects.filter(
                exercise=exercise,
                workout_history__session=obj.session  # Ensure this references the correct session
            ).exclude(workout_history=obj)

            # Get the maximum previous weight lifted for the same exercise
            previous_max_weight = previous_performances.aggregate(max_weight=models.Max('actual_kg'))['max_weight'] or 0

            # Calculate weight difference if there's progress overload
            weight_difference = current_kg - previous_max_weight if current_kg > previous_max_weight else 0

        # Return only the weight difference as an integer
        return weight_difference




    def get_workout_time(self, obj):
        workout_duration = obj.workout_time
        if workout_duration is None:
            return "0h 0m 0s"  # Default if no workout time

        hours, remainder = divmod(workout_duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
