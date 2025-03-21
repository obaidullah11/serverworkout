# from django.contrib import admin
# from .models import BodyPartMeasurement,CoreMeasurement,WorkoutHistory,SetHistory,Workout, workoutExercise, Set, WorkoutSession, SetPerformance,Folder


# @admin.register(CoreMeasurement)
# class CoreMeasurementAdmin(admin.ModelAdmin):
#     list_display = ('device_id', 'waist_circumference', 'hip_circumference', 'chest_circumference')
#     search_fields = ('device_id',)  # Enable search by device_id
#     ordering = ('device_id',)  # Order by device_id by default
#     list_filter = ('device_id',)  # Add filter options by device_id

# @admin.register(BodyPartMeasurement)
# class BodyPartMeasurementAdmin(admin.ModelAdmin):
#     list_display = ('device_id', 'arm_circumference', 'thigh_circumference', 'calf_circumference')
#     search_fields = ('device_id',)  # Enable search by device_id
#     ordering = ('device_id',)  # Order by device_id by default
#     list_filter = ('device_id',)  # Add filter options by device_id

# @admin.register(WorkoutHistory)
# class WorkoutHistoryAdmin(admin.ModelAdmin):
#     list_display = ('device_id', 'workout', 'session', 'highest_weight', 'best_performance_set', 'created_at')
#     search_fields = ('device_id', 'workout__name')  # Allow searching by device ID and workout name

# @admin.register(SetHistory)
# class SetHistoryAdmin(admin.ModelAdmin):
#     list_display = ('workout_history', 'exercise', 'set_number', 'actual_kg', 'actual_reps', 'created_at')
#     search_fields = ('workout_history__device_id', 'exercise__name')  # Allow searching by device ID and exercise name
# @admin.register(Folder)
# class FolderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name','color','device_id', 'created_at')  # Fields to display in the list view
#     search_fields = ('name',)  # Enable search by folder name
# @admin.register(Workout)
# class WorkoutAdmin(admin.ModelAdmin):
#     list_display = ('id','name', 'device_id', 'created_at')  # Fields to display in the list view
#     search_fields = ('name', 'device_id')  # Enable search by workout name and user
#     list_filter = ('created_at',)  # Enable filtering by creation date

 # Enable search by workout and exercise names

#
from django.contrib import admin
from django.utils.html import format_html
# from import_export.admin import ExportMixin

from .models import (
    Folder, Workout, workoutExercise, Set, SetPerformance,
    WorkoutSession, WorkoutHistory, SetHistory,
    CoreMeasurement, BodyPartMeasurement
)
@admin.register(workoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'exercise', 'order')  # Display workout name, exercise, and order
    search_fields = ('workout__name', 'exercise__name')
# Folder Admin


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
    list_display = ('session', 'session_date', 'created_at_formatted', 'set', 'actual_kg', 'actual_reps')
    search_fields = ('session__workout__name', 'set__perform_exercise__exercise__name')

    def session_date(self, obj):
        return obj.session.date.strftime('%Y-%m-%d')  # Format the session date as ISO (YYYY-MM-DD)

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')  # Format `created_at` nicely
    created_at_formatted.short_description = 'Created At'

    session_date.short_description = 'Session Date'  # Column header in the admin interface


class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "created_at")
    search_fields = ("name", "device_id")
    list_filter = ("created_at",)
    ordering = ("-created_at",)  # Order folders by creation date in descending order

# Workout Admin
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "folder", "created_at")
    search_fields = ("name", "device_id", "folder__name")
    list_filter = ("created_at", "folder")
    fieldsets = (
        ("Workout Details", {"fields": ("name", "device_id", "folder", "notes")}),
    )
    ordering = ("-created_at",)  # Order workouts by creation date in descending order

class SetHistoryInline(admin.TabularInline):
    model = SetHistory
    extra = 1  # Number of empty forms to display by default
    fields = ('exercise', 'set_number', 'actual_kg', 'actual_reps', 'rm', 'pr')  # Fields to display in inline form
    readonly_fields = ('created_at',)  # Optionally make created_at readonly

# WorkoutHistory Admin
class WorkoutHistoryAdmin(admin.ModelAdmin):
    list_display = ("device_id", "get_workout_name", "highest_weight", "workout_time", "created_at")
    search_fields = ("device_id", "workout__name")
    list_filter = ("created_at",)
    fieldsets = (
        ("History Details", {"fields": ("device_id", "workout", "highest_weight", "workout_time")}),
        ("Best Performance", {"fields": ( "best_performance_set",)}),
    )
    inlines = [SetHistoryInline]  # Add the SetHistory inline to the WorkoutHistory admin
    ordering = ("-created_at",)  # Order workout histories by creation date in descending order

    def get_workout_name(self, obj):
        return obj.workout.name  # Access the related Workout model's 'name' field
    get_workout_name.admin_order_field = 'workout__name'  # Allows sorting by this field
    get_workout_name.short_description = 'Workout Name'  # Customize the column header

class BodyPartMeasurementAdmin(admin.ModelAdmin):
    list_display = ("device_id", "arm_circumference", "thigh_circumference", "calf_circumference")
    ordering = ("-device_id",)  # Order body part measurements by device_id in descending order

# Core Measurement Admin
class CoreMeasurementAdmin(admin.ModelAdmin):
    list_display = ("device_id", "waist_circumference", "hip_circumference", "chest_circumference")
    ordering = ("-device_id",)  # Order core measurements by device_id in descending order

# Register models at the end
admin.site.register(Folder, FolderAdmin)
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(WorkoutHistory, WorkoutHistoryAdmin)
admin.site.register(BodyPartMeasurement, BodyPartMeasurementAdmin)
admin.site.register(CoreMeasurement, CoreMeasurementAdmin)
