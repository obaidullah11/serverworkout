from rest_framework import status, generics
from rest_framework.response import Response
from decimal import Decimal
from rest_framework.views import APIView
from collections import defaultdict
from django.db.models import Max
from rest_framework.decorators import api_view
from .models import Workout, WorkoutSession, SetPerformance, Workout, workoutExercise, Set, SetPerformance,Folder,WorkoutHistory,SetHistory
from .serializers import WorkoutHistorySerializer,WorkoutSerializernew,FolderSerializernew,FolderSerializer, WorkoutSerializer, UpdateProgressSerializer, SetPerformanceSerializerNew
from datetime import timedelta
from django.db import models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CoreMeasurement, BodyPartMeasurement
from .serializers import CoreMeasurementSerializer, BodyPartMeasurementSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CoreMeasurement, BodyPartMeasurement
from .serializers import CoreMeasurementSerializer, BodyPartMeasurementSerializer

class MeasurementUpdateAPIView(APIView):
    def patch(self, request, device_id):
        # Retrieve core measurement
        try:
            core_measurement = CoreMeasurement.objects.get(device_id=device_id)
        except CoreMeasurement.DoesNotExist:
            return Response({
                "success": False,
                "message": "CoreMeasurement not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Update core measurement
        core_serializer = CoreMeasurementSerializer(core_measurement, data=request.data.get('core_measurement'), partial=True)
        if core_serializer.is_valid():
            core_serializer.save()  # Save updates
        else:
            return Response({
                "success": False,
                "message": "Validation errors occurred for core measurement.",
                "data": core_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve body part measurement
        try:
            body_part_measurement = BodyPartMeasurement.objects.get(device_id=device_id)
        except BodyPartMeasurement.DoesNotExist:
            return Response({
                "success": False,
                "message": "BodyPartMeasurement not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Update body part measurement
        body_serializer = BodyPartMeasurementSerializer(body_part_measurement, data=request.data.get('body_part_measurement'), partial=True)
        if body_serializer.is_valid():
            body_serializer.save()  # Save updates
        else:
            return Response({
                "success": False,
                "message": "Validation errors occurred for body part measurement.",
                "data": body_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": "Measurements updated successfully.",
            "data": {
                'core_measurement': core_serializer.data,
                'body_part_measurement': body_serializer.data
            }
        }, status=status.HTTP_200_OK)

class MeasurementRetrieveAPIView(APIView):
    def get(self, request, device_id):
        # Retrieve core measurement
        try:
            core_measurement = CoreMeasurement.objects.get(device_id=device_id)
            core_serializer = CoreMeasurementSerializer(core_measurement)
        except CoreMeasurement.DoesNotExist:
            return Response({
                "success": False,
                "message": "CoreMeasurement not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Retrieve body part measurement
        try:
            body_part_measurement = BodyPartMeasurement.objects.get(device_id=device_id)
            body_serializer = BodyPartMeasurementSerializer(body_part_measurement)
        except BodyPartMeasurement.DoesNotExist:
            return Response({
                "success": False,
                "message": "BodyPartMeasurement not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "message": "Measurements retrieved successfully.",
            "data": {
                'core_measurement': core_serializer.data,
                'body_part_measurement': body_serializer.data
            }
        }, status=status.HTTP_200_OK)

class MeasurementCreateAPIView(APIView):
    def post(self, request, device_id):
        core_data = request.data.get('core_measurement')
        body_data = request.data.get('body_part_measurement')
        
        # Validate and save core measurement
        core_serializer = CoreMeasurementSerializer(data=core_data)
        if core_serializer.is_valid():
            core_measurement = core_serializer.save(device_id=device_id)  # Set device_id from URL
        else:
            return Response({
                "success": False,
                "message": "Validation errors occurred for core measurement.",
                "data": core_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save body part measurement
        body_serializer = BodyPartMeasurementSerializer(data=body_data)
        if body_serializer.is_valid():
            body_part_measurement = body_serializer.save(device_id=device_id)  # Use same device_id from URL
        else:
            return Response({
                "success": False,
                "message": "Validation errors occurred for body part measurement.",
                "data": body_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": "Measurements created successfully.",
            "data": {
                'core_measurement': core_serializer.data,
                'body_part_measurement': body_serializer.data
            }
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_workout_by_session(request, session_id):
    try:
        # Fetch the workout session based on the session_id
        workout_session = WorkoutSession.objects.get(id=session_id)

        # Retrieve the associated workout
        workout = workout_session.workout

        # Serialize the workout data
        serializer = WorkoutSerializernew(workout)
        serialized_workout = serializer.data

        # Add previous performance data to each workout's exercises
        for exercise in serialized_workout['perform_exercises']:
            for set_data in exercise['sets']:
                set_id = set_data['id']

                # Get the last SetPerformance record for this session and set
                set_performance = SetPerformance.objects.filter(session__id=session_id, set__id=set_id).last()

                if set_performance:
                    # If a performance is found, add the performance data under 'previous'
                    set_data['previous'] = {
                        'actual_kg': set_performance.actual_kg,
                        'actual_reps': set_performance.actual_reps
                    }
                else:
                    # No performance data found
                    set_data['previous'] = {}

        return Response({
            "status": True,
            "message": "Workout data retrieved successfully by session ID.",
            "data": serialized_workout
        }, status=status.HTTP_200_OK)

    except WorkoutSession.DoesNotExist:
        return Response({
            "status": False,
            "message": "No workout found for this session ID.",
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)
class DeleteWorkoutHistoryView(APIView):
    def delete(self, request, pk):
        try:
            # Try to find the WorkoutHistory by primary key
            workout_history = WorkoutHistory.objects.get(pk=pk)
            workout_history.delete()

            # Return success response
            return Response({
                "success": True,
                "message": "Workout history deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)

        except WorkoutHistory.DoesNotExist:
            # If the WorkoutHistory does not exist, return failure response
            return Response({
                "success": False,
                "message": "Workout history not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle unexpected errors
            return Response({
                "success": False,
                "message": f"An error occurred: {str(e)}",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FolderByDeviceIDView(generics.ListAPIView):
    def get(self, request, device_id, *args, **kwargs):
        # Fetch all folders associated with the given device_id
        folders = Folder.objects.filter(device_id=device_id)

        if not folders.exists():
            return Response({
                "status": False,
                "message": "No folders found for this device.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        # Prepare the data response
        folder_data = []
        for folder in folders:
            folder_dict = {
                "id": folder.id,
                "name": folder.name,
                "created_at": folder.created_at,
                "device_id": folder.device_id,
                "workouts": []
            }

            # Fetch workouts under each folder
            workouts = Workout.objects.filter(folder=folder)
            for workout in workouts:
                workout_dict = {
                    "id": workout.id,
                    "name": workout.name,
                    "created_at": workout.created_at,
                    "perform_exercises": []
                }

                # Fetch exercises related to the workout
                exercises = workoutExercise.objects.filter(workout=workout)
                for exercise in exercises:
                    exercise_dict = {
                        "exercise_id": exercise.exercise.id,
                        "exercise_name": exercise.exercise.name,
                        "order": exercise.order,
                        "sets": []
                    }

                    # Fetch sets related to each exercise
                    sets = Set.objects.filter(workoutExercise=exercise)
                    for workout_set in sets:
                        set_dict = {
                            "set_id": workout_set.id,
                            "set_number": workout_set.set_number,
                            "kg": workout_set.kg,
                            "reps": workout_set.reps,
                            "previous_performance": {}
                        }

                        # Fetch the previous performance for the set
                        previous_performance = SetPerformance.objects.filter(set=workout_set).order_by('-session__date').first()

                        if previous_performance:
                            set_dict["previous_performance"] = {
                                "actual_kg": previous_performance.actual_kg,
                                "actual_reps": previous_performance.actual_reps
                            }

                        exercise_dict["sets"].append(set_dict)

                    workout_dict["perform_exercises"].append(exercise_dict)

                folder_dict["workouts"].append(workout_dict)

            folder_data.append(folder_dict)

        # Return the folder data with workouts, exercises, and previous performance data
        return Response({
            "status": True,
            "message": "Folders and associated workouts with previous performance data retrieved successfully.",
            "data": folder_data
        }, status=status.HTTP_200_OK)




# class FolderByDeviceIDView(generics.ListAPIView):
#     serializer_class = FolderSerializernew

#     def get(self, request, device_id, *args, **kwargs):
#         # Fetch folders by device_id
#         folders = Folder.objects.filter(device_id=device_id)

#         # If no folders are found, return a 404 response
#         if not folders.exists():
#             return Response({
#                 "status": False,
#                 "message": "No folders found for this device.",
#                 "data": []
#             }, status=status.HTTP_404_NOT_FOUND)

#         # Serialize the folder data
#         serializer = FolderSerializernew(folders, many=True)
#         return Response({
#             "status": True,
#             "message": "Folders retrieved successfully.",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)

class CreateFolderView(generics.CreateAPIView):
    serializer_class = FolderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        folder = serializer.save()

        return Response({
            "status": True,
            "message": "Folder created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
class CreateWorkoutView(APIView):
    def post(self, request, *args, **kwargs):
        print(f"Request Data: {request.data}")  # Debugging print
        serializer = WorkoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Workout created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        print(f"Errors: {serializer.errors}")  # Debugging print
        return Response({
            "status": False,
            "message": "Failed to create workout.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_user_workouts(request, device_id):
#     # Fetch workouts related to the device_id directly
#     workouts = Workout.objects.filter(device_id=device_id)

#     # If no workouts are found, return a 404 response
#     if not workouts.exists():
#         return Response({
#             "status": False,
#             "message": "No workouts found for this device.",
#             "data": []
#         }, status=status.HTTP_404_NOT_FOUND)

#     # Serialize the workout data
#     serializer = WorkoutSerializernew(workouts, many=True)
#     serialized_workouts = serializer.data

#     # Add previous performance data to each workout's exercises
#     for workout in serialized_workouts:
#         session_id = workout.get('session_id')

#         for exercise in workout['perform_exercises']:
#             for set_data in exercise['sets']:
#                 set_id = set_data['id']

#                 # Get the last SetPerformance record for this session and set
#                 set_performance = SetPerformance.objects.filter(session__id=session_id, set__id=set_id).last()

#                 if set_performance:
#                     # If a performance is found, add the performance data under 'previous'
#                     set_data['previous'] = {
#                         'actual_kg': set_performance.actual_kg,
#                         'actual_reps': set_performance.actual_reps
#                     }
#                 else:
#                     # No performance data found
#                     set_data['previous'] = {}

#     # Debugging info
#     print(f"Device ID: {device_id}, Number of workouts: {workouts.count()}")

#     return Response({
#         "status": True,
#         "message": "User workouts retrieved successfully.",
#         "data": serialized_workouts
#     }, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_user_workouts(request, device_id):
    # Fetch workouts related to the device_id directly
    workouts = Workout.objects.filter(device_id=device_id)

    # If no workouts are found, return a 404 response
    if not workouts.exists():
        return Response({
            "status": False,
            "message": "No workouts found for this device.",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    # Serialize the workout data
    serializer = WorkoutSerializernew(workouts, many=True)
    serialized_workouts = serializer.data

    # Organize workouts by folder
    folder_wise_workouts = defaultdict(list)

    # Add previous performance data to each workout's exercises
    for workout in serialized_workouts:
        session_id = workout.get('session_id')

        for exercise in workout['perform_exercises']:
            for set_data in exercise['sets']:
                set_id = set_data['id']

                # Get the last SetPerformance record for this session and set
                set_performance = SetPerformance.objects.filter(session__id=session_id, set__id=set_id).last()

                if set_performance:
                    # If a performance is found, add the performance data under 'previous'
                    set_data['previous'] = {
                        'actual_kg': set_performance.actual_kg,
                        'actual_reps': set_performance.actual_reps
                    }
                else:
                    # No performance data found
                    set_data['previous'] = {}

        # Append the workout to the corresponding folder in folder_wise_workouts
        folder_name = workout.get('folder', 'Uncategorized')
        folder_wise_workouts[folder_name].append(workout)

    # Convert defaultdict to regular dict for JSON serialization
    folder_wise_workouts = dict(folder_wise_workouts)

    return Response({
        "status": True,
        "message": "User workouts retrieved successfully.",
        "data": folder_wise_workouts
    }, status=status.HTTP_200_OK)
class UpdateWorkoutProgressView(generics.CreateAPIView):
    serializer_class = UpdateProgressSerializer

    def post(self, request, device_id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print(serializer.errors)  # Debugging line
            return Response({"status": False, "message": "Invalid data.", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']
        performances = serializer.validated_data['performances']
        workout_time_str = request.data.get('workout_time')

        workout_time = self.parse_workout_time(workout_time_str)

        workout_session = WorkoutSession.objects.filter(id=session_id, device_id=device_id).first()
        if not workout_session:
            return Response({"status": False, "message": "Workout session not found."}, status=status.HTTP_404_NOT_FOUND)

        highest_weight = 0
        best_performance_set = None
        max_rm = 0
        new_pr_flag = False

        for performance in performances:
            set_id = performance['set']
            actual_kg = performance['actual_kg']
            actual_reps = performance['actual_reps']

            set_performance, created = SetPerformance.objects.update_or_create(
                session=workout_session,
                set_id=set_id,
                defaults={'actual_kg': actual_kg, 'actual_reps': actual_reps}
            )

            if actual_kg > highest_weight:
                highest_weight = actual_kg
                best_performance_set = set_performance

            rm = actual_kg * (1 + actual_reps / 30)

            if rm > max_rm:
                max_rm = rm

            previous_set_performances = SetPerformance.objects.filter(
                set_id=set_id, session__device_id=device_id
            ).exclude(session=workout_session)
            previous_max_weight = previous_set_performances.aggregate(max_weight=models.Max('actual_kg'))['max_weight'] or 0

            if actual_kg > previous_max_weight:
                new_pr_flag = True

        if not best_performance_set:
            return Response({"status": False, "message": "No valid performances found."}, status=status.HTTP_400_BAD_REQUEST)

        workout_history = WorkoutHistory.objects.create(
            device_id=device_id,
            workout=workout_session.workout,
            session=workout_session,
            highest_weight=highest_weight,
            best_performance_set=best_performance_set,
            workout_time=workout_time
        )

        set_history_data = []
        for performance in performances:
            set_id = performance['set']
            actual_kg = performance['actual_kg']
            actual_reps = performance['actual_reps']

            workout_set = Set.objects.get(id=set_id)
            rm = actual_kg * (1 + actual_reps / 30)

            previous_set_performances = SetPerformance.objects.filter(
                set_id=set_id, session__device_id=device_id
            ).exclude(session=workout_session)
            previous_max_weight = previous_set_performances.aggregate(max_weight=models.Max('actual_kg'))['max_weight'] or 0
            pr = 1 if actual_kg > previous_max_weight else 0

            set_history = SetHistory.objects.create(
                workout_history=workout_history,
                exercise=workout_set.workoutExercise.exercise,
                set_number=workout_set.set_number,
                actual_kg=actual_kg,
                actual_reps=actual_reps,
                rm=rm,
                pr=pr
            )

            set_history_data.append({
                "exercise": workout_set.workoutExercise.exercise.name,
                "set_number": workout_set.set_number,
                "actual_kg": actual_kg,
                "actual_reps": actual_reps,
                "rm": round(rm, 2),
                "pr": pr
            })

        response_data = {
            "status": True,
            "message": "Progress updated successfully.",
            "workout_name": workout_session.workout.name,
            "date_time": workout_history.created_at.isoformat(),
            "total_weight": highest_weight,
            "max_rm": round(max_rm, 2),
            "new_pr": new_pr_flag,
            "workout_time": str(workout_time),
            "exercise_details": set_history_data
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def parse_workout_time(self, workout_time_str):
        try:
            h, m, s = map(int, workout_time_str.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError:
            return timedelta(0)

class GetSetPerformanceByUserView(generics.ListAPIView):
    serializer_class = SetPerformanceSerializerNew

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        # Get all workout sessions for the user
        workout_sessions = WorkoutSession.objects.filter(user_id=user_id)

        # Check if the user has workout sessions
        if not workout_sessions.exists():
            return SetPerformance.objects.none()

        # Return all SetPerformance objects related to the user's workout sessions
        return SetPerformance.objects.filter(session__in=workout_sessions)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "status": False,
                "message": "No set performances found for this user.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": True,
            "message": "Set performances retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UpdateWorkoutView(APIView):
    def put(self, request, *args, **kwargs):
        workout_id = kwargs.get('pk')  # Get the workout ID from the URL

        try:
            workout = Workout.objects.get(id=workout_id)
        except Workout.DoesNotExist:
            return Response({
                "status": False,
                "message": "Workout not found."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkoutSerializernew(workout, data=request.data, partial=True)  # Enable partial update

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Workout updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "message": "Failed to update workout.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class WorkoutHistoryByDeviceView(generics.ListAPIView):
    serializer_class = WorkoutHistorySerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')
        return WorkoutHistory.objects.filter(device_id=device_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": False, "message": "No workout history found for this device."}, status=status.HTTP_404_NOT_FOUND)


import calendar
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
from django.db.models import Max
from rest_framework import generics
from rest_framework.response import Response
from .models import WorkoutHistory, SetPerformance
from .serializers import WorkoutHistorySerializer

# class ExerciseRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id, exercise_id):
#         # Get all workout histories for the given device_id and exercise_id
#         workout_histories = WorkoutHistory.objects.filter(
#             device_id=device_id,
#             session__set_performances__set__workoutExercise__exercise_id=exercise_id
#         ).distinct()  # Ensure distinct workout histories

#         # Initialize response structure
#         response_data = {
#             "success": True,
#             "data": {
#                 "history": [],
#                 "records": {
#                     "max_weight": 0,
#                     "max_volume": 0,
#                     "max_reps": 0,
#                     "record_history": []
#                 },
#                 "charts": []  # To store chart data
#             }
#         }

#         # Prepare the history and records data
#         for workout_history in workout_histories:
#             # Prepare history details for a unique workout
#             set_performances = SetPerformance.objects.filter(
#                 session=workout_history.session,
#                 set__workoutExercise__exercise_id=exercise_id
#             )

#             total_weight = sum(sp.actual_kg for sp in set_performances)
#             total_reps = sum(sp.actual_reps for sp in set_performances)

#             # Initialize the history data
#             history_data = {
#                 "workout_name": workout_history.workout.name,
#                 "exercise_name": set_performances.first().set.workoutExercise.exercise.name if set_performances.exists() else "Unknown",
#                 "performed_time": workout_history.created_at,
#                 "workout_time": workout_history.workout_time / 60,  # Convert seconds to minutes
#                 "total_weight": total_weight,  # Total weight for the workout
#                 "total_reps": total_reps,      # Total reps for the workout
#                 "sets": []
#             }

#             for set_performance in set_performances:
#                 history_data["sets"].append({
#                     "set_number": set_performance.set.set_number,
#                     "actual_kg": set_performance.actual_kg,
#                     "actual_reps": set_performance.actual_reps,
#                 })

#             # Append history data to response
#             response_data["data"]["history"].append(history_data)

#             # Prepare records data
#             max_weight = set_performances.aggregate(Max('actual_kg'))['actual_kg__max'] or 0
#             max_reps = set_performances.aggregate(Max('actual_reps'))['actual_reps__max'] or 0
#             max_volume = sum(sp.actual_kg * sp.actual_reps for sp in set_performances)

#             # Update collective max_weight, max_volume, and max_reps
#             response_data["data"]["records"]["max_weight"] = max(
#                 response_data["data"]["records"]["max_weight"],
#                 max_weight
#             )
#             response_data["data"]["records"]["max_reps"] = max(
#                 response_data["data"]["records"]["max_reps"],
#                 max_reps
#             )
#             response_data["data"]["records"]["max_volume"] += max_volume

#             # Prepare detailed record history
#             for set_performance in set_performances:
#                 predicted_weight = self.predict_weight(set_performance)
#                 response_data["data"]["records"]["record_history"].append({
#                     "exercise": set_performance.set.workoutExercise.exercise.name,
#                     "set_number": set_performance.set.set_number,
#                     "actual_kg": set_performance.actual_kg,
#                     "actual_reps": set_performance.actual_reps,
#                     "predicted_weight": predicted_weight
#                 })

#         # Add weekly and monthly chart data
#         self.add_chart_data(response_data, workout_histories)

#         return Response(response_data)

#     def predict_weight(self, set_performance):
#         # Predict weight logic
#         return set_performance.actual_kg * Decimal('1.1')  # Predicting a 10% increase
#     def add_chart_data(self, response_data, workout_histories):
#     # Chart data structure
#         weekly_data = {}
#         monthly_data = {}

#         for workout_history in workout_histories:
#             # Get week start date (Monday)
#             week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())
#             month_year = workout_history.created_at.strftime('%Y-%m')

#             # Weekly chart data
#             if week_start not in weekly_data:
#                 weekly_data[week_start] = 0
#             weekly_data[week_start] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

#             # Monthly chart data
#             if month_year not in monthly_data:
#                 monthly_data[month_year] = 0
#             monthly_data[month_year] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

#         # Prepare weekly chart response data
#         weekly_chart_data = [
#             {"x": week_start.isoformat(), "y": weight}
#             for week_start, weight in sorted(weekly_data.items())
#         ]

#         # Prepare monthly chart response data
#         monthly_chart_data = [
#             {"x": month_year, "y": monthly_data[month_year]}
#             for month_year in sorted(monthly_data.keys())
#         ]

#         # Add charts to response with isPremium flag
#         response_data["data"]["charts"].append({
#             "graph_title": "Cardio Weekly Activity",
#             "graph_subtitle": "Weekly Weight Lifted",
#             "type": "weekly",
#             "isPremium": False,  # isPremium for weekly chart
#             "data": weekly_chart_data
#         })

#         response_data["data"]["charts"].append({
#             "graph_title": "Cardio Monthly Activity",
#             "graph_subtitle": "Monthly Weight Lifted",
#             "type": "monthly",
#             "isPremium": True,  # isPremium for monthly chart
#             "data": monthly_chart_data
#         })

#         # def add_chart_data(self, response_data, workout_histories):
#         #     # Chart data structure
#         #     weekly_data = {}
#         #     monthly_data = {}

#         #     for workout_history in workout_histories:
#         #         # Get week start date (Monday)
#         #         week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())
#         #         month_year = workout_history.created_at.strftime('%Y-%m')

#         #         # Weekly chart data
#         #         if week_start not in weekly_data:
#         #             weekly_data[week_start] = 0
#         #         weekly_data[week_start] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

#         #         # Monthly chart data
#         #         if month_year not in monthly_data:
#         #             monthly_data[month_year] = 0
#         #         monthly_data[month_year] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

#         #     # Prepare weekly chart response data
#         #     weekly_chart_data = [
#         #         {"x": (week_start + timedelta(days=day)).isoformat(), "y": weekly_data.get(week_start + timedelta(days=day), 0)}
#         #         for day in range(7)
#         #     ]

#         #     # Prepare monthly chart response data
#         #     monthly_chart_data = [
#         #         {"x": month_year, "y": monthly_data.get(month_year, 0)}
#         #         for month_year in sorted(monthly_data.keys())
#         #     ]

#         #     # Add charts to response with isPremium flag
#         #     response_data["data"]["charts"].append({
#         #         "graph_title": "Cardio Weekly Activity",
#         #         "graph_subtitle": "Weekly Weight Lifted",
#         #         "type": "weekly",
#         #         "isPremium": False,  # isPremium for weekly chart
#         #         "data": weekly_chart_data
#         #     })

#         #     response_data["data"]["charts"].append({
#         #         "graph_title": "Cardio Monthly Activity",
#         #         "graph_subtitle": "Monthly Weight Lifted",
#         #         "type": "monthly",
#         #         "isPremium": True,  # isPremium for monthly chart
#         #         "data": monthly_chart_data
#         #     })




class ExerciseRecordsView(generics.GenericAPIView):
    serializer_class = WorkoutHistorySerializer

    def get(self, request, device_id, exercise_id):
        # Get all workout histories for the given device_id and exercise_id
        workout_histories = WorkoutHistory.objects.filter(
            device_id=device_id,
            session__set_performances__set__workoutExercise__exercise_id=exercise_id
        ).distinct()  # Ensure distinct workout histories

        # Initialize response structure
        response_data = {
            "status": True,
            "data": []
        }

        # Prepare the history, records, and charts data
        for workout_history in workout_histories:
            set_performances = SetPerformance.objects.filter(
                session=workout_history.session,
                set__workoutExercise__exercise_id=exercise_id
            )

            # Aggregate total weight, reps, and max weight for each workout
            total_weight = set_performances.aggregate(total_weight=Sum('actual_kg'))['total_weight'] or 0
            total_reps = set_performances.aggregate(total_reps=Sum('actual_reps'))['total_reps'] or 0
            max_weight = set_performances.aggregate(Max('actual_kg'))['actual_kg__max'] or 0
            max_reps = set_performances.aggregate(Max('actual_reps'))['actual_reps__max'] or 0
            max_volume = sum(Decimal(sp.actual_kg) * Decimal(sp.actual_reps) for sp in set_performances)

            # Convert workout time to a readable format
            workout_time_seconds = workout_history.workout_time.total_seconds() if isinstance(workout_history.workout_time, timedelta) else workout_history.workout_time
            formatted_workout_time = str(timedelta(seconds=int(workout_time_seconds)))

            # Initialize history data for this workout
            history_data = {
                "id": workout_history.id,
                "device_id": workout_history.device_id,
                "workout_name": workout_history.workout.name,
                "highest_weight": f"{max_weight:.2f}",
                "set_history_data": [],
                "created_at": workout_history.created_at.isoformat(),
                "maxweight": max_weight,
                "PRs": max_reps,
                "workout_time": formatted_workout_time
            }

            # Populate set history for each set performance
            for set_performance in set_performances:
                rm = Decimal(set_performance.actual_kg) * (1 + Decimal(set_performance.actual_reps) / Decimal(30))  # Example RM calculation
                history_data["set_history_data"].append({
                    "exercise_name": set_performance.set.workoutExercise.exercise.name,
                    "set_number": set_performance.set.set_number,
                    "actual_kg": float(set_performance.actual_kg),
                    "actual_reps": set_performance.actual_reps,
                    "rm": float(rm)
                })

            # Add the history data to response
            response_data["data"].append(history_data)

        # Add records data
        response_data["records"] = {
            "max_weight": max(weight for weight in [history_data["highest_weight"] for history_data in response_data["data"]] or [0]),
            "max_volume": sum(history_data["maxweight"] for history_data in response_data["data"]),
            "max_reps": max(history_data["PRs"] for history_data in response_data["data"]),
            "record_history": [
                {
                    "exercise": set_performance.set.workoutExercise.exercise.name,
                    "set_number": set_performance.set.set_number,
                    "actual_kg": float(set_performance.actual_kg),
                    "actual_reps": set_performance.actual_reps,
                    "predicted_weight": self.predict_weight(set_performance)
                }
                for workout_history in workout_histories
                for set_performance in SetPerformance.objects.filter(session=workout_history.session, set__workoutExercise__exercise_id=exercise_id)
            ]
        }

        # Add chart data
        self.add_chart_data(response_data, workout_histories)

        return Response(response_data)

    def predict_weight(self, set_performance):
        # Predict weight with an example of a 10% increase
        return float(Decimal(set_performance.actual_kg) * Decimal('1.1'))

    def add_chart_data(self, response_data, workout_histories):
        weekly_data = {}
        monthly_data = {}

        for workout_history in workout_histories:
            # Calculate weekly start date and month-year
            week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())
            month_year = workout_history.created_at.strftime('%Y-%m')

            # Populate weekly data
            if week_start not in weekly_data:
                weekly_data[week_start] = 0
            weekly_data[week_start] += sum(float(sp.actual_kg) for sp in SetPerformance.objects.filter(session=workout_history.session))

            # Populate monthly data
            if month_year not in monthly_data:
                monthly_data[month_year] = 0
            monthly_data[month_year] += sum(float(sp.actual_kg) for sp in SetPerformance.objects.filter(session=workout_history.session))

        # Weekly chart data response
        response_data["charts"] = [
            {
                "graph_title": "Cardio Weekly Activity",
                "graph_subtitle": "Weekly Weight Lifted",
                "type": "weekly",
                "isPremium": False,
                "data": [{"x": week_start.isoformat(), "y": weight} for week_start, weight in sorted(weekly_data.items())]
            },
            {
                "graph_title": "Cardio Monthly Activity",
                "graph_subtitle": "Monthly Weight Lifted",
                "type": "monthly",
                "isPremium": True,
                "data": [{"x": month_year, "y": weight} for month_year, weight in sorted(monthly_data.items())]
            }
        ]
