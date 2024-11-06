from django.contrib import admin
from .models import BodyPartMeasurement,CoreMeasurement,WorkoutHistory,SetHistory,Workout, workoutExercise, Set, WorkoutSession, SetPerformance,Folder


@admin.register(CoreMeasurement)
class CoreMeasurementAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'waist_circumference', 'hip_circumference', 'chest_circumference')
    search_fields = ('device_id',)  # Enable search by device_id
    ordering = ('device_id',)  # Order by device_id by default
    list_filter = ('device_id',)  # Add filter options by device_id

@admin.register(BodyPartMeasurement)
class BodyPartMeasurementAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'arm_circumference', 'thigh_circumference', 'calf_circumference')
    search_fields = ('device_id',)  # Enable search by device_id
    ordering = ('device_id',)  # Order by device_id by default
    list_filter = ('device_id',)  # Add filter options by device_id

@admin.register(WorkoutHistory)
class WorkoutHistoryAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'workout', 'session', 'highest_weight', 'best_performance_set', 'created_at')
    search_fields = ('device_id', 'workout__name')  # Allow searching by device ID and workout name

@admin.register(SetHistory)
class SetHistoryAdmin(admin.ModelAdmin):
    list_display = ('workout_history', 'exercise', 'set_number', 'actual_kg', 'actual_reps', 'created_at')
    search_fields = ('workout_history__device_id', 'exercise__name')  # Allow searching by device ID and exercise name
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','device_id', 'created_at')  # Fields to display in the list view
    search_fields = ('name',)  # Enable search by folder name
@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'device_id', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'device_id')  # Enable search by workout name and user
    list_filter = ('created_at',)  # Enable filtering by creation date

@admin.register(workoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'exercise', 'order')  # Display workout name, exercise, and order
    search_fields = ('workout__name', 'exercise__name')  # Enable search by workout and exercise names

@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('id','workoutExercise', 'set_number', 'kg', 'reps')  # Display set info
    search_fields = ('workoutExercise__workout__name', 'workoutExercise__exercise__name')  # Enable search by workout and exercise names

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('id','device_id', 'workout', 'date')  # Display user, workout, and session date
    search_fields = ('device_id', 'workout__name')  # Enable search by username and workout name
    list_filter = ('date',)  # Enable filtering by session date

@admin.register(SetPerformance)
class SetPerformanceAdmin(admin.ModelAdmin):
    list_display = ('session', 'set', 'actual_kg', 'actual_reps')  # Display session, set, actual kg, and reps
    search_fields = ('session__workout__name', 'set__perform_exercise__exercise__name')  # Enable search by workout and exercise names
