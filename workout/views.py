from rest_framework import status, generics
from rest_framework.response import Response
from decimal import Decimal
from rest_framework.views import APIView
from django.db.models import Max
from train.models import Exercise
from rest_framework.decorators import api_view
from .models import BodyPartMeasurement,CoreMeasurement,Workout, WorkoutSession, SetPerformance, Workout, workoutExercise, Set, SetPerformance,Folder,WorkoutHistory,SetHistory
from .serializers import CoreMeasurementSerializer,BodyPartMeasurementSerializer,WorkoutHistorySerializer,WorkoutSerializernew,FolderSerializernew,FolderSerializer, WorkoutSerializer, UpdateProgressSerializer, SetPerformanceSerializerNew
from datetime import timedelta
from users.models import PremiumProfile
from django.db import models
import random
from rest_framework import generics, status
from rest_framework.response import Response

from collections import defaultdict
from datetime import datetime, timedelta
from .models import WorkoutHistory, SetHistory

from collections import defaultdict
from datetime import datetime, timedelta


import requests















# from products.models import Product
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# from  import PaymentService
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@csrf_exempt
def delete_workout(request, pk):
    if request.method == 'POST':
        try:
            workout = get_object_or_404(Workout, pk=pk)
            workout.delete()
            return JsonResponse({
                'success': True,
                'data': None,
                'message': 'Workout deleted successfully'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'data': None,
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False,
        'data': None,
        'message': 'Method not allowed'
    }, status=405)
@csrf_exempt  # Exempt from CSRF verification since this is a callback from an external service
def post_payment_result(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Log the received data or handle it
            print("Received data:", data)

            # Extract transaction status and other relevant details
            status = data.get('status')
            transaction_id = data.get('id')
            order_id = data.get('reference', {}).get('order')

            # Handle success or failure based on status
            if status == 'CAPTURED':
                # Transaction is successful, process accordingly
                print(f"Transaction {transaction_id} for order {order_id} was successful.")
                # Update your database with the success status, etc.
            else:
                # Transaction failed or is pending, handle the failure case
                print(f"Transaction {transaction_id} for order {order_id} failed or pending.")
                # Handle failure, notify the user, update the database, etc.

            # Return a response indicating that the post was received successfully
            return JsonResponse({'message': 'Received post data successfully'})

        except Exception as e:
            print(f"Error processing payment result: {e}")
            return JsonResponse({'message': 'Error processing payment result'}, status=500)
    else:
        # If the request method is not POST, return an error
        return JsonResponse({'message': 'Invalid request method'}, status=405)



from django.http import HttpResponse
import requests
import json

def payment_result(request):
    # Extract `tap_id` from the query string
    tap_id = request.GET.get('tap_id')

    if not tap_id:
        return HttpResponse("Missing tap_id parameter", status=400)

    # Use the `tap_id` to retrieve transaction details from Tap API
    api_url = f"https://api.tap.company/v2/charges/{tap_id}"
    headers = {
        'Authorization': 'Bearer sk_test_7zBjytrV2gnmK3ZaCAuQT4wP'  # Replace with your actual secret key
    }

    # Send a GET request to the Tap API to retrieve the charge details
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        try:
            # Attempt to parse the API response as JSON
            transaction_details = response.json()

            # Extract useful transaction details
            status = transaction_details.get("status")
            amount = transaction_details.get("amount")
            currency = transaction_details.get("currency")
            error_message = transaction_details.get("response", {}).get("message", "No error message")
            customer_info = transaction_details.get("customer", {})
            customer_name = f"{customer_info.get('first_name')} {customer_info.get('last_name')}"
            customer_email = customer_info.get("email")
            customer_phone = customer_info.get("phone", {}).get("number", "No phone number")

            # Pass data to the template
            context = {
                'status': status,
                'amount': amount,
                'currency': currency,
                'error_message': error_message,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone
            }

            # Render the result in an HTML template
            return render(request, 'workout/payment_result.html', context)

        except json.JSONDecodeError:
            return HttpResponse("Error decoding JSON response from Tap API", status=500)
    else:
        return HttpResponse(f"Failed to retrieve transaction: {response.text}", status=500)


@csrf_exempt
def create_charge(request):
    if request.method == 'POST':
        try:
            # Parse the incoming request data
            data = json.loads(request.body)
            print("Received data:", data)  # Debugging log for received data

            # Fetch the last transaction ID and order ID using your "last transaction" API
            last_transaction_response = requests.get('https://taptradebackend.pythonanywhere.com/api/trade/api/last-transaction/')
            print("Last transaction response text:", last_transaction_response.text)  # Log the response
            if last_transaction_response.status_code == 200:
                try:
                    last_transaction = last_transaction_response.json()
                    next_transaction_id = f"txn_{int(last_transaction['transaction_id'].split('_')[1]) + 1}"
                    next_order_id = f"ord_{int(last_transaction['order_id'].split('_')[1]) + 1}"
                except (ValueError, KeyError, IndexError):
                    next_transaction_id = "txn_1"
                    next_order_id = "ord_1"
            else:
                next_transaction_id = "txn_1"
                next_order_id = "ord_1"

            # Prepare the data in the format required by Tap API
            charge_data = {
                "amount": data.get('amount', 1),  # Default to 1 if not provided
                "currency": "SAR",  # Default currency is SAR
                "customer_initiated": data.get('customer_initiated', True),  # Default to True if not provided
                "threeDSecure": True,  # Default 3DSecure to True
                "save_card": False,  # Default save_card to False
                "description": "Test transaction for payment",  # Default description
                "metadata": {"udf1": "Custom data"},  # Default metadata
                "reference": {
                    "transaction": next_transaction_id,  # Use next transaction ID
                    "order": next_order_id  # Use next order ID
                },
                "receipt": {
                    "email": True,  # Default to True for email receipt
                    "sms": True  # Default to True for SMS receipt
                },
                "customer": {
                    "first_name": data.get('customer_first_name', 'John'),
                    "middle_name": data.get('customer_middle_name', 'Doe'),
                    "last_name": data.get('customer_last_name', 'Smith'),
                    "email": data.get('customer_email', 'john.doe@example.com'),
                    "phone": {
                        "country_code": data.get('customer_phone_country_code', 965),
                        "number": data.get('customer_phone_number', '51234567')
                    }
                },
                "merchant": {
                    "id": "1234"  # Static merchant ID
                },
                "source": {
                    "id": "src_all"  # Static source ID
                },
                "post": {
                    "url": "https://mfarhanakram.eu.pythonanywhere.com/payment/post_result/"  # Default post URL
                },
                "redirect": {
                    "url": "https://mfarhanakram.eu.pythonanywhere.com/payment/result/"  # Default redirect URL
                }
            }

            # Print the charge data being sent to Tap API
            print("Prepared charge data:", json.dumps(charge_data, indent=4))

            # Send the API request to Tap API
            url = 'https://api.tap.company/v2/charges/'
            headers = {
                'Authorization': 'Bearer sk_test_7zBjytrV2gnmK3ZaCAuQT4wP',  # Replace with your actual API key
                'accept': 'application/json',
                'content-type': 'application/json'
            }

            # Make the POST request to Tap API
            response = requests.post(url, json=charge_data, headers=headers)
            print("API response status code:", response.status_code)  # Print the status code
            print("API response body:", response.text)  # Print the response body

            # Handle empty or invalid responses
            try:
                tap_response_data = response.json()
            except ValueError:
                return JsonResponse({"error": "Invalid response from Tap API", "details": response.text}, status=response.status_code)

            if response.status_code == 200:
                # Save the new transaction using your "create transaction" API
                create_transaction_data = {
                    "transaction_id": next_transaction_id,
                    "order_id": next_order_id,
                    "amount": data.get('amount', 1),
                    "currency": "SAR"
                }
                create_transaction_response = requests.post(
                    'https://taptradebackend.pythonanywhere.com/api/trade/api/create-transaction/',
                    json=create_transaction_data
                )
                print("Create transaction response text:", create_transaction_response.text)  # Log the response

                if create_transaction_response.status_code != 201:
                    return JsonResponse({"error": "Failed to save transaction via API", "details": create_transaction_response.text}, status=400)

                # Return the API response
                return JsonResponse(tap_response_data, status=200)
            else:
                return JsonResponse({"error": "Failed to create charge", "details": response.text}, status=response.status_code)

        except Exception as e:
            print("Error occurred:", str(e))  # Print the error message if an exception is raised
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)


































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

# class FolderByDeviceIDView(generics.ListAPIView):
#     def get(self, request, device_id, *args, **kwargs):
#         # Fetch all folders associated with the given device_id
#         folders = Folder.objects.filter(device_id=device_id)

#         if not folders.exists():
#             return Response({
#                 "status": False,
#                 "message": "No folders found for this device.",
#                 "data": []
#             }, status=status.HTTP_404_NOT_FOUND)

#         # Prepare the data response
#         folder_data = []
#         for folder in folders:
#             folder_dict = {
#                 "id": folder.id,
#                 "name": folder.name,
#                 "created_at": folder.created_at,
#                 "device_id": folder.device_id,
#                 "workouts": []
#             }

#             # Fetch workouts under each folder
#             workouts = Workout.objects.filter(folder=folder)
#             for workout in workouts:
#                 workout_dict = {
#                     "id": workout.id,
#                     "name": workout.name,
#                     "created_at": workout.created_at,
#                     "perform_exercises": []
#                 }

#                 # Fetch exercises related to the workout
#                 exercises = workoutExercise.objects.filter(workout=workout)
#                 for exercise in exercises:
#                     exercise_dict = {
#                         "exercise_id": exercise.exercise.id,
#                         "exercise_name": exercise.exercise.name,
#                         "order": exercise.order,
#                         "sets": []
#                     }

#                     # Fetch sets related to each exercise
#                     sets = Set.objects.filter(workoutExercise=exercise)
#                     for workout_set in sets:
#                         set_dict = {
#                             "set_id": workout_set.id,
#                             "set_number": workout_set.set_number,
#                             "kg": workout_set.kg,
#                             "reps": workout_set.reps,
#                             "previous_performance": {}
#                         }

#                         # Fetch the previous performance for the set
#                         previous_performance = SetPerformance.objects.filter(set=workout_set).order_by('-session__date').first()

#                         if previous_performance:
#                             set_dict["previous_performance"] = {
#                                 "actual_kg": previous_performance.actual_kg,
#                                 "actual_reps": previous_performance.actual_reps
#                             }

#                         exercise_dict["sets"].append(set_dict)

#                     workout_dict["perform_exercises"].append(exercise_dict)

#                 folder_dict["workouts"].append(workout_dict)

#             folder_data.append(folder_dict)

#         # Return the folder data with workouts, exercises, and previous performance data
#         return Response({
#             "status": True,
#             "message": "Folders and associated workouts with previous performance data retrieved successfully.",
#             "data": folder_data
#         }, status=status.HTTP_200_OK)
from django.http import JsonResponse
from django.views import View
class FolderByDeviceIDView(View):
    def get(self, request, device_id):
        """
        Retrieve folders and associated workouts for a given device ID.
        If no folders exist or example_workouts is empty, seed default data.
        """
        folders = Folder.objects.filter(device_id=device_id)

        if not folders.exists():
            self.seed_default_data(device_id)
            folders = Folder.objects.filter(device_id=device_id)

        folder_data = []
        example_workouts = []

        for folder in folders:
            workouts = Workout.objects.filter(folder=folder)
            formatted_workouts = []

            for workout in workouts:
                # Fetch the latest session for this workout
                workout_session = WorkoutSession.objects.filter(workout=workout).order_by('-id').first()

                workout_dict = {
                    "id": workout.id,
                    "name": workout.name,
                    "notes":workout.notes,
                    "created_at": workout.created_at,
                    "session_id": workout_session.id if workout_session else None,  # Include session ID
                    "perform_exercises": []
                }

                exercises = workoutExercise.objects.filter(workout=workout)
                for exercise in exercises:
                    exercise_dict = {
                        "exercise_id": exercise.exercise.id,
                        "exercise_name": exercise.exercise.name,
                        "order": exercise.order,
                        "sets": []
                    }

                    sets = Set.objects.filter(workoutExercise=exercise)
                    for workout_set in sets:
                        set_dict = {
                            "set_id": workout_set.id,
                            "set_number": workout_set.set_number,
                            "kg": workout_set.kg,
                            "reps": workout_set.reps,
                            "previous_performance": {}
                        }

                        previous_performance = SetPerformance.objects.filter(set=workout_set).order_by('-session__date').first()
                        if previous_performance:
                            set_dict["previous_performance"] = {
                                "actual_kg": previous_performance.actual_kg,
                                "actual_reps": previous_performance.actual_reps
                            }

                        exercise_dict["sets"].append(set_dict)

                    workout_dict["perform_exercises"].append(exercise_dict)

                formatted_workouts.append(workout_dict)

            if folder.name == "Default Folder":
                example_workouts.extend(formatted_workouts)
            else:
                folder_data.append({
                    "id": folder.id,
                    "name": folder.name,
                    "created_at": folder.created_at,
                    # "notes":workout.notes,
                    "device_id": folder.device_id,
                    "workouts": formatted_workouts
                })

        # Check if example_workouts is still empty after initial retrieval
        if not example_workouts:
            self.seed_default_data(device_id)
            return self.get(request, device_id)  # Recursively fetch data again after seeding

        return JsonResponse({
            "status": "success",
            "example_workouts": example_workouts,
            "folders": folder_data
        })

    def seed_default_data(self, device_id):
        """
        Seeds default folders, workouts, exercises, and sets for a new device ID.
        """
        folder = Folder.objects.create(name="Default Folder", device_id=device_id)

        workout1 = Workout.objects.create(folder=folder, name="Full Body Workout", device_id=device_id,notes="A balanced full-body workout focusing on strength and endurance.")
        workout2 = Workout.objects.create(folder=folder, name="Cardio Session", device_id=device_id,notes="A high-intensity cardio session to boost stamina and burn calories.")

        # Create WorkoutSessions for these workouts
        workout_session1 = WorkoutSession.objects.create(workout=workout1, device_id=device_id)
        workout_session2 = WorkoutSession.objects.create(workout=workout2, device_id=device_id)

        default_exercises = Exercise.objects.all()[:3]  # Select first 3 exercises
        cardio_exercises = Exercise.objects.all()[3:6]  # Select next 3 exercises for Cardio

        # Add exercises and sets for Full Body Workout
        for index, exercise in enumerate(default_exercises, start=1):
            w_exercise = workoutExercise.objects.create(workout=workout1, exercise=exercise, order=index)

            Set.objects.create(workoutExercise=w_exercise, set_number=1, kg=20.0, reps=10)
            Set.objects.create(workoutExercise=w_exercise, set_number=2, kg=25.0, reps=8)
            Set.objects.create(workoutExercise=w_exercise, set_number=3, kg=30.0, reps=6)

        # 🔥 Add exercises and sets for Cardio Session
        for index, exercise in enumerate(cardio_exercises, start=1):
            w_exercise = workoutExercise.objects.create(workout=workout2, exercise=exercise, order=index)

            # Cardio exercises may have reps but no weights
            Set.objects.create(workoutExercise=w_exercise, set_number=1, kg=0.0, reps=15)
            Set.objects.create(workoutExercise=w_exercise, set_number=2, kg=0.0, reps=20)
            Set.objects.create(workoutExercise=w_exercise, set_number=3, kg=0.0, reps=25)

        print(f"✅ Seeded default data for device_id: {device_id}")



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
def generate_random_color():
    """Generate a random hex color code."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

class CreateFolderView(generics.CreateAPIView):
    serializer_class = FolderSerializer

    def perform_create(self, serializer):
        random_color = generate_random_color()
        serializer.save(color=random_color)  # Explicitly set color_code

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": True,
            "message": "Folder created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
# class CreateFolderView(generics.CreateAPIView):
#     serializer_class = FolderSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         folder = serializer.save()

#         return Response({
#             "status": True,
#             "message": "Folder created successfully.",
#             "data": serializer.data
        # }, status=status.HTTP_201_CREATED)
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

#     # Add workout_id and previous performance data to each workout's exercises
#     for workout, workout_obj in zip(serialized_workouts, workouts):
#         # Include the workout ID
#         workout['workout_id'] = workout_obj.id

#         # Process each exercise for previous performance data
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
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)

    # Serialize the workout data
    serializer = WorkoutSerializernew(workouts, many=True)
    serialized_workouts = serializer.data

    # Add workout_id and previous performance data to each workout's exercises
    for workout, workout_obj in zip(serialized_workouts, workouts):
        # Include the workout ID
        workout['workout_id'] = workout_obj.id

        # Process each exercise for previous performance data
        session_id = workout.get('session_id')
        unique_exercises = {}  # Dictionary to track unique exercises

        for exercise in workout['perform_exercises']:
            exercise_id = exercise['exercise']['id']
            if exercise_id not in unique_exercises:
                unique_exercises[exercise_id] = exercise  # Only add the exercise if not already added

                # Fetch and add the previous performance data
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

        # Now update 'perform_exercises' with the unique exercises
        workout['perform_exercises'] = list(unique_exercises.values())

    return Response({
        "status": True,
        "message": "User workouts retrieved successfully.",
        "data": serialized_workouts
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

            # Add previous performance data to each workout's exercises
            serialized_workout = serializer.data
            session_id = serialized_workout.get('session_id')

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
                "message": "Workout updated successfully.",
                "data": serialized_workout
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

    # def add_chart_data(self, response_data, workout_histories):
    # # Chart data structure
    #     weekly_data = {}
    #     monthly_data = {}

    #     for workout_history in workout_histories:
    #         # Get week start date (Monday) and reset time to midnight
    #         week_start = (workout_history.created_at - timedelta(days=workout_history.created_at.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    #         month_year = workout_history.created_at.strftime('%Y-%m')

    #         # Calculate total weight for the current session
    #         total_weight = sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

    #         # Weekly chart data (sum if the date already exists)
    #         if week_start in weekly_data:
    #             weekly_data[week_start] += total_weight
    #         else:
    #             weekly_data[week_start] = total_weight

    #         # Monthly chart data (sum if the month already exists)
    #         if month_year in monthly_data:
    #             monthly_data[month_year] += total_weight
    #         else:
    #             monthly_data[month_year] = total_weight

    #     # Prepare weekly chart response data
    #     weekly_chart_data = [
    #         {"x": week_start.isoformat(), "y": weight}
    #         for week_start, weight in sorted(weekly_data.items())
    #     ]

    #     # Prepare monthly chart response data
    #     monthly_chart_data = [
    #         {"x": month_year, "y": monthly_data[month_year]}
    #         for month_year in sorted(monthly_data.keys())
    #     ]

    #     # Add charts to response with isPremium flag
    #     response_data["data"]["charts"].append({
    #         "graph_title": "Cardio Weekly Activity",
    #         "graph_subtitle": "Weekly Weight Lifted",
    #         "type": "weekly",
    #         "isPremium": False,  # isPremium for weekly chart
    #         "data": weekly_chart_data
    #     })

    #     response_data["data"]["charts"].append({
    #         "graph_title": "Cardio Monthly Activity",
    #         "graph_subtitle": "Monthly Weight Lifted",
    #         "type": "monthly",
    #         "isPremium": True,  # isPremium for monthly chart
    #         "data": monthly_chart_data
    #     })

    # def add_chart_data(self, response_data, workout_histories):
    # # Chart data structure
    #     weekly_data = {}
    #     monthly_data = {}

    #     for workout_history in workout_histories:
    #         # Get week start date (Monday)
    #         week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())
    #         month_year = workout_history.created_at.strftime('%Y-%m')

    #         # Weekly chart data
    #         if week_start not in weekly_data:
    #             weekly_data[week_start] = 0
    #         weekly_data[week_start] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

    #         # Monthly chart data
    #         if month_year not in monthly_data:
    #             monthly_data[month_year] = 0
    #         monthly_data[month_year] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

    #     # Prepare weekly chart response data
    #     weekly_chart_data = [
    #         {"x": week_start.isoformat(), "y": weight}
    #         for week_start, weight in sorted(weekly_data.items())
    #     ]

    #     # Prepare monthly chart response data
    #     monthly_chart_data = [
    #         {"x": month_year, "y": monthly_data[month_year]}
    #         for month_year in sorted(monthly_data.keys())
    #     ]

    #     # Add charts to response with isPremium flag
    #     response_data["data"]["charts"].append({
    #         "graph_title": "Cardio Weekly Activity",
    #         "graph_subtitle": "Weekly Weight Lifted",
    #         "type": "weekly",
    #         "isPremium": False,  # isPremium for weekly chart
    #         "data": weekly_chart_data
    #     })

    #     response_data["data"]["charts"].append({
    #         "graph_title": "Cardio Monthly Activity",
    #         "graph_subtitle": "Monthly Weight Lifted",
    #         "type": "monthly",
    #         "isPremium": True,  # isPremium for monthly chart
    #         "data": monthly_chart_data
    #     })





































        # def add_chart_data(self, response_data, workout_histories):
        #     # Chart data structure
        #     weekly_data = {}
        #     monthly_data = {}

        #     for workout_history in workout_histories:
        #         # Get week start date (Monday)
        #         week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())
        #         month_year = workout_history.created_at.strftime('%Y-%m')

        #         # Weekly chart data
        #         if week_start not in weekly_data:
        #             weekly_data[week_start] = 0
        #         weekly_data[week_start] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

        #         # Monthly chart data
        #         if month_year not in monthly_data:
        #             monthly_data[month_year] = 0
        #         monthly_data[month_year] += sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

        #     # Prepare weekly chart response data
        #     weekly_chart_data = [
        #         {"x": (week_start + timedelta(days=day)).isoformat(), "y": weekly_data.get(week_start + timedelta(days=day), 0)}
        #         for day in range(7)
        #     ]

        #     # Prepare monthly chart response data
        #     monthly_chart_data = [
        #         {"x": month_year, "y": monthly_data.get(month_year, 0)}
        #         for month_year in sorted(monthly_data.keys())
        #     ]

        #     # Add charts to response with isPremium flag
        #     response_data["data"]["charts"].append({
        #         "graph_title": "Cardio Weekly Activity",
        #         "graph_subtitle": "Weekly Weight Lifted",
        #         "type": "weekly",
        #         "isPremium": False,  # isPremium for weekly chart
        #         "data": weekly_chart_data
        #     })

        #     response_data["data"]["charts"].append({
        #         "graph_title": "Cardio Monthly Activity",
        #         "graph_subtitle": "Monthly Weight Lifted",
        #         "type": "monthly",
        #         "isPremium": True,  # isPremium for monthly chart
        #         "data": monthly_chart_data
        #     })

# class ExerciseWidjetRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id, exercise_id):
#         # Retrieve the exercise name based on exercise_id
#         try:
#             exercise_name = Exercise.objects.get(id=exercise_id).name
#         except Exercise.DoesNotExist:
#             return Response({"status": False, "error": "Exercise not found."}, status=404)

#         # Get all workout histories for the given device_id and exercise_id
#         workout_histories = WorkoutHistory.objects.filter(
#             device_id=device_id,
#             session__set_performances__set__workoutExercise__exercise_id=exercise_id
#         ).distinct()  # Ensure distinct workout histories

#         # Initialize response structure
#         response_data = {
#             "status": True,
#             "data": []
#         }

#         # Add chart data with dynamic exercise name in graph title
#         self.add_chart_data(response_data, workout_histories, exercise_name)

#         return Response(response_data)

#     def add_chart_data(self, response_data, workout_histories, exercise_name):
#         weekly_data = {}

#         for workout_history in workout_histories:
#             # Calculate weekly start date
#             week_start = workout_history.created_at - timedelta(days=workout_history.created_at.weekday())

#             # Populate weekly data
#             if week_start not in weekly_data:
#                 weekly_data[week_start] = 0
#             weekly_data[week_start] += sum(float(sp.actual_kg) for sp in SetPerformance.objects.filter(session=workout_history.session))

#         # Weekly chart data with dynamic title
#         response_data["charts"] = [
#             {
#                 "graph_title": f"{exercise_name} Weekly Activity",  # Dynamic exercise name in title
#                 "graph_subtitle": f"{exercise_name} Weekly Lifted",
#                 "type": "weekly",
#                 "isPremium": False,
#                 "data": [{"x": week_start.isoformat(), "y": weight} for week_start, weight in sorted(weekly_data.items())]
#             }
#         ]

# class ExerciseWidjetRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id):
#         # Get all workout histories for the given device_id
#         workout_histories = WorkoutHistory.objects.filter(device_id=device_id).distinct()

#         # Initialize response structure, including 'charts' and 'message'
#         response_data = {
#             "status": True,
#             "message": "Collective performance data retrieved successfully.",
#             "data": [],
#             "charts": []
#         }

#         # Step 1: Collect and aggregate weekly data across all exercises
#         self.add_collective_chart_data(response_data, workout_histories)

#         return Response(response_data)

#     def add_collective_chart_data(self, response_data, workout_histories):
#         weekly_data = {}

#         # Step 2: Gather SetPerformance records associated with the given workout histories
#         set_performances = SetPerformance.objects.filter(
#             session__in=workout_histories.values_list('session', flat=True)
#         ).select_related('session', 'set').distinct()

#         # Step 3: Aggregate actual_kg for all exercises into weekly data
#         for performance in set_performances:
#             # Calculate the start of the week for the workout session
#             week_start = performance.session.created_at - timedelta(days=performance.session.created_at.weekday())

#             # Accumulate the weekly lifted weight
#             if week_start not in weekly_data:
#                 weekly_data[week_start] = 0
#             weekly_data[week_start] += float(performance.actual_kg)

#         # Step 4: Add a single collective chart to the response
#         response_data["charts"].append(
#             {
#                 "graph_title": "Collective Weekly Activity",
#                 "graph_subtitle": "Total Weight Lifted Weekly",
#                 "type": "weekly",
#                 "isPremium": False,
#                 "data": [{"x": week_start.isoformat(), "y": weight} for week_start, weight in sorted(weekly_data.items())]
#             }
#         )
# class ExerciseWidjetRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id):
#         # Get all workout histories for the given device_id
#         workout_histories = WorkoutHistory.objects.filter(device_id=device_id).distinct()

#         # Initialize response structure, including 'charts'
#         response_data = {
#             "status": True,
#             "data": [],
#             "charts": []  # Initialize 'charts' as an empty list
#         }

#         # Step 1: Get all exercises related to this device's workout histories by finding relevant SetPerformances
#         set_performances = SetPerformance.objects.filter(
#             session__workouthistory__device_id=device_id
#         ).distinct()

#         # Get unique exercises linked through WorkoutExercise
#         exercises = Exercise.objects.filter(
#             id__in=set_performances.values_list('set__workoutExercise__exercise', flat=True).distinct()
#         )

#         # Step 2: For each exercise, calculate weekly data and add to the response
#         for exercise in exercises:
#             self.add_chart_data(response_data, workout_histories, exercise)

#         return Response(response_data)

#     def add_chart_data(self, response_data, workout_histories, exercise):
#         weekly_data = {}

#         # Step 3: Filter SetPerformance records that link to the exercise through WorkoutExercise and device workout histories
#         exercise_sessions = SetPerformance.objects.filter(
#             session__in=workout_histories.values_list('session', flat=True),
#             set__workoutExercise__exercise=exercise
#         ).select_related('session', 'set').distinct()

#         for performance in exercise_sessions:
#             # Calculate weekly start date for the workout session
#             week_start = performance.session.created_at - timedelta(days=performance.session.created_at.weekday())

#             # Populate weekly data for this exercise
#             if week_start not in weekly_data:
#                 weekly_data[week_start] = 0
#             weekly_data[week_start] += float(performance.actual_kg)

#         # Append weekly chart data for this exercise to the 'charts' list in the response
#         response_data["charts"].append(
#             {
#                 "graph_title": f"{exercise.name} Weekly Activity",
#                 "graph_subtitle": f"{exercise.name} Weekly Lifted",
#                 "type": "weekly",
#                 "isPremium": False,
#                 "data": [{"x": week_start.isoformat(), "y": weight} for week_start, weight in sorted(weekly_data.items())]
#             }
#         )
from collections import defaultdict
from datetime import datetime, timedelta
from django.http import JsonResponse
class ExerciseWidjetRecordsView(APIView):
    def get(self, request, device_id):
        # Initialize response data structure
        response_data = {
            "status": True,
            "message": "data retrieved successfully.",
            "data": []
        }

        # Check if the device belongs to a premium user
        is_premium = PremiumProfile.objects.filter(device_id=device_id, is_premium=True).exists()

        # Determine the start and end of the current week (Monday-Sunday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        try:
            # Get all WorkoutHistory for the given device_id within the current week
            workout_histories = WorkoutHistory.objects.filter(
                device_id=device_id,
                created_at__date__gte=start_of_week,
                created_at__date__lte=end_of_week
            ).order_by('created_at')

            exercises_data = defaultdict(list)

            # Serialize and group data by exercise and date
            for history in workout_histories:
                serializer = WorkoutHistorySerializer(history)
                set_history_data = serializer.data.get('set_history_data', [])

                for item in set_history_data:
                    exercise_name = item['exercise_name']

                    try:
                        actual_kg = float(item['actual_kg'])  # Convert to float
                    except (TypeError, ValueError):
                        actual_kg = 0.0

                    created_at = history.created_at

                    # Group by exercise name and timestamp
                    exercises_data[exercise_name].append((created_at, actual_kg))

            # Prepare charts with aggregated data
            charts = []
            for exercise, records in exercises_data.items():
                aggregated_data = defaultdict(float)

                for timestamp, kg in records:
                    # Sum weights for identical timestamps (group by just the date)
                    date_key = timestamp.date()
                    aggregated_data[date_key] += kg

                # Construct the chart data
                charts.append({
                    "graph_title": f"{exercise} Weekly Activity",
                    "graph_subtitle": f"{exercise} Weekly Lifted",
                    "type": "weekly",
                    "isPremium": is_premium,
                    "data": [
                        {
                            "x": date.isoformat() + f"{date.strftime('%H:%M:%S.%f')}+00:00",
                            "y": sum_weights
                        }
                        for date, sum_weights in sorted(aggregated_data.items())
                    ]
                })

            # Add charts to response data
            response_data["data"] = charts

            return Response(response_data, status=status.HTTP_200_OK)

        except WorkoutHistory.DoesNotExist:
            return Response({
                "status": False,
                "message": "No performance data found for this device.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
# class ExerciseWidjetRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id):
#         # Check if the device_id is a premium user
#         is_premium = PremiumProfile.objects.filter(device_id=device_id, is_premium=True).exists()

#         # Determine the start and end of the current week (Monday to Sunday)
#         today = datetime.now().date()
#         start_of_week = today - timedelta(days=today.weekday())
#         end_of_week = start_of_week + timedelta(days=6)

#         # Get all workout histories for the given device_id within the current week
#         workout_histories = WorkoutHistory.objects.filter(
#             device_id=device_id,
#             created_at__date__gte=start_of_week,
#             created_at__date__lte=end_of_week
#         ).distinct()

#         # Initialize response structure
#         response_data = {
#             "status": True,
#             "data": [],
#             "charts": []
#         }

#         # Get all exercises related to this device's workout histories
#         set_performances = SetPerformance.objects.filter(
#             session__workouthistory__device_id=device_id
#         ).distinct()

#         exercises = Exercise.objects.filter(
#             id__in=set_performances.values_list('set__workoutExercise__exercise', flat=True).distinct()
#         )

#         # For each exercise, calculate weekly data and add it to the response
#         for exercise in exercises:
#             self.add_chart_data(response_data, workout_histories, exercise, is_premium)

#         return Response(response_data)

#     def add_chart_data(self, response_data, workout_histories, exercise, is_premium):
#         exercises_data = defaultdict(list)

#         # Filter sessions that link the exercise through WorkoutExercise and workout histories
#         exercise_sessions = SetPerformance.objects.filter(
#             session__in=workout_histories.values_list('session', flat=True),
#             set__workoutExercise__exercise=exercise
#         ).select_related('session', 'set').distinct()

#         # Group data by exercise name and timestamps
#         for performance in exercise_sessions:
#             created_at = performance.session.created_at
#             actual_kg = float(performance.actual_kg) if performance.actual_kg else 0.0
#             exercises_data[exercise.name].append((created_at, actual_kg))

#         weekly_data = {}

#         # Aggregate data for chart visualization
#         for exercise_name, records in exercises_data.items():
#             aggregated_data = defaultdict(float)

#             for timestamp, kg in records:
#                 date_key = timestamp.date()

#                 aggregated_data[date_key] += kg

#             response_data['charts'].append({
#                 "graph_title": f"{exercise_name} Weekly Activity",
#                 "graph_subtitle": f"{exercise_name} Weekly Lifted",
#                 "type": "weekly",
#                 "isPremium": is_premium,
#                 "data": [{"x": date.isoformat(), "y": weight} for date, weight in sorted(aggregated_data.items())]
#             })

# class ExerciseWidjetRecordsView(generics.GenericAPIView):
#     serializer_class = WorkoutHistorySerializer

#     def get(self, request, device_id):
#         # Check if the device_id is a premium user
#         is_premium = PremiumProfile.objects.filter(device_id=device_id, is_premium=True).exists()

#         # Get all workout histories for the given device_id
#         workout_histories = WorkoutHistory.objects.filter(device_id=device_id).distinct()

#         # Initialize response structure, including 'charts'
#         response_data = {
#             "status": True,
#             "data": [],
#             "charts": []  # Initialize 'charts' as an empty list
#         }

#         # Step 1: Get all exercises related to this device's workout histories by finding relevant SetPerformances
#         set_performances = SetPerformance.objects.filter(
#             session__workouthistory__device_id=device_id
#         ).distinct()

#         # Get unique exercises linked through WorkoutExercise
#         exercises = Exercise.objects.filter(
#             id__in=set_performances.values_list('set__workoutExercise__exercise', flat=True).distinct()
#         )

#         # Step 2: For each exercise, calculate weekly data and add to the response
#         for exercise in exercises:
#             self.add_chart_data(response_data, workout_histories, exercise, is_premium)

#         return Response(response_data)

#     def add_chart_data(self, response_data, workout_histories, exercise, is_premium):
#         weekly_data = {}

#         # Step 3: Filter SetPerformance records that link to the exercise through WorkoutExercise and device workout histories
#         exercise_sessions = SetPerformance.objects.filter(
#             session__in=workout_histories.values_list('session', flat=True),
#             set__workoutExercise__exercise=exercise
#         ).select_related('session', 'set').distinct()

#         for performance in exercise_sessions:
#             # Calculate weekly start date for the workout session
#             week_start = performance.session.created_at - timedelta(days=performance.session.created_at.weekday())

#             # Populate weekly data for this exercise
#             if week_start not in weekly_data:
#                 weekly_data[week_start] = 0
#             weekly_data[week_start] += float(performance.actual_kg)

#         # Append weekly chart data for this exercise to the 'charts' list in the response
#         response_data["charts"].append(
#             {
#                 "graph_title": f"{exercise.name} Weekly Activity",
#                 "graph_subtitle": f"{exercise.name} Weekly Lifted",
#                 "type": "weekly",
#                 "isPremium": is_premium,  # Use the `is_premium` flag determined earlier
#                 "data": [{"x": week_start.isoformat(), "y": weight} for week_start, weight in sorted(weekly_data.items())]
#             }
#         )
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
from datetime import timedelta, datetime
import datetime
from collections import defaultdict
from collections import defaultdict
from dateutil.relativedelta import relativedelta

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
            "success": True,
            "data": {
                "history": [],
                "records": {
                    "max_weight": 0,
                    "max_volume": 0,
                    "max_reps": 0,
                    "record_history": []
                },
                "charts": []  # To store chart data
            }
        }

        # Prepare the history and records data
        for workout_history in workout_histories:
            # Prepare history details for a unique workout
            set_performances = SetPerformance.objects.filter(
                session=workout_history.session,
                set__workoutExercise__exercise_id=exercise_id
            )

            total_weight = sum(sp.actual_kg for sp in set_performances)
            total_reps = sum(sp.actual_reps for sp in set_performances)

            # Initialize the history data
            history_data = {
                "workout_name": workout_history.workout.name,
                "exercise_name": set_performances.first().set.workoutExercise.exercise.name if set_performances.exists() else "Unknown",
                "performed_time": workout_history.created_at,
                "workout_time": workout_history.workout_time / 60,  # Convert seconds to minutes
                "total_weight": total_weight,  # Total weight for the workout
                "total_reps": total_reps,      # Total reps for the workout
                "sets": []
            }

            for set_performance in set_performances:
                history_data["sets"].append({
                    "set_number": set_performance.set.set_number,
                    "actual_kg": set_performance.actual_kg,
                    "actual_reps": set_performance.actual_reps,
                })

            # Append history data to response
            response_data["data"]["history"].append(history_data)

            # Prepare records data
            max_weight = set_performances.aggregate(Max('actual_kg'))['actual_kg__max'] or 0
            max_reps = set_performances.aggregate(Max('actual_reps'))['actual_reps__max'] or 0
            max_volume = sum(sp.actual_kg * sp.actual_reps for sp in set_performances)

            # Update collective max_weight, max_volume, and max_reps
            response_data["data"]["records"]["max_weight"] = max(
                response_data["data"]["records"]["max_weight"],
                max_weight
            )
            response_data["data"]["records"]["max_reps"] = max(
                response_data["data"]["records"]["max_reps"],
                max_reps
            )
            response_data["data"]["records"]["max_volume"] += max_volume

            # Prepare detailed record history
            for set_performance in set_performances:
                predicted_weight = self.predict_weight(set_performance)
                response_data["data"]["records"]["record_history"].append({
                    "exercise": set_performance.set.workoutExercise.exercise.name,
                    "set_number": set_performance.set.set_number,
                    "actual_kg": set_performance.actual_kg,
                    "actual_reps": set_performance.actual_reps,
                    "predicted_weight": predicted_weight
                })

        # Add weekly and monthly chart data
        self.add_chart_data(response_data, workout_histories)

        return Response(response_data)

    def predict_weight(self, set_performance):
        # Predict weight logic
        return set_performance.actual_kg * Decimal('1.1')  # Predicting a 10% increase







    def add_chart_data(self, response_data, workout_histories):
        weekly_data = defaultdict(int)
        monthly_data = defaultdict(int)

        if not workout_histories.exists():
            return

        # Sort workout histories by date
        all_dates = [wh.created_at.date() for wh in workout_histories]
        min_date, max_date = min(all_dates), max(all_dates)

        # Get the current week's start (Monday) and end (Sunday)
        today = datetime.date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Fill weekly data with current week's dates
        current_date = start_of_week
        while current_date <= end_of_week:
            weekly_data[current_date] = 0
            current_date += timedelta(days=1)

        # Generate all months for the current year
        for month in range(1, 13):
            month_str = f"{min_date.year}-{month:02d}"
            monthly_data[month_str] = 0

        # Populate actual data from workout histories
        for workout_history in workout_histories:
            date = workout_history.created_at.date()
            month_year = workout_history.created_at.strftime('%Y-%m')

            total_weight = sum(sp.actual_kg for sp in SetPerformance.objects.filter(session=workout_history.session))

            # Add data to weekly chart only if within the current week
            if start_of_week <= date <= end_of_week:
                weekly_data[date] += total_weight

            monthly_data[month_year] += total_weight

        # Generate chart data
        weekly_chart_data = [{"x": date.strftime('%Y-%m-%d'), "y": weight} for date, weight in weekly_data.items()]
        monthly_chart_data = [{"x": month, "y": weight} for month, weight in sorted(monthly_data.items())]

        response_data["data"]["charts"].append({
            "graph_title": "Cardio Weekly Activity",
            "graph_subtitle": "Weekly Weight Lifted",
            "type": "weekly",
            "isPremium": False,
            "data": weekly_chart_data
        })

        response_data["data"]["charts"].append({
            "graph_title": "Cardio Monthly Activity",
            "graph_subtitle": "Monthly Weight Lifted",
            "type": "monthly",
            "isPremium": True,
            "data": monthly_chart_data
        })
