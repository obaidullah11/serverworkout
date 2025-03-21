from django.urls import path
from .views import delete_workout,post_payment_result,payment_result,create_charge,ExerciseWidjetRecordsView,MeasurementUpdateAPIView,MeasurementRetrieveAPIView,MeasurementCreateAPIView,get_workout_by_session,DeleteWorkoutHistoryView,ExerciseRecordsView,WorkoutHistoryByDeviceView, UpdateWorkoutView, CreateFolderView,CreateWorkoutView,FolderByDeviceIDView,get_user_workouts,UpdateWorkoutProgressView,GetSetPerformanceByUserView

urlpatterns = [
    path('measurements/update/<str:device_id>/', MeasurementUpdateAPIView.as_view(), name='measurements-update'),  # New update endpoint
    path('measurements/get/<str:device_id>/', MeasurementRetrieveAPIView.as_view(), name='measurements-retrieve'),
    path('measurements/<str:device_id>/', MeasurementCreateAPIView.as_view(), name='measurements-create'),
    path('workouts/create/', CreateWorkoutView.as_view(), name='create_workout'),
    path('user/<str:device_id>/workouts/', get_user_workouts, name='get_user_workouts'),
    path('api/workout/sessions/<str:device_id>/', GetSetPerformanceByUserView.as_view(), name='get-workout-sessions'),
    path('api/workout/update-progress/<str:device_id>/', UpdateWorkoutProgressView.as_view(), name='update-workout-progress'),
    path('api/folder/create/', CreateFolderView.as_view(), name='create-folder'),
    path('api/folders/<str:device_id>/', FolderByDeviceIDView.as_view(), name='folders-by-device-id'),
    path('api/workout/update/<int:pk>/', UpdateWorkoutView.as_view(), name='update-workout'),
    path('api/workout/history/<str:device_id>/', WorkoutHistoryByDeviceView.as_view(), name='workout-history-by-device'),
    path('exercise-records/<str:device_id>/<int:exercise_id>/', ExerciseRecordsView.as_view(), name='exercise-records'),
    path('workout-history/delete/<int:pk>/', DeleteWorkoutHistoryView.as_view(), name='delete_workout_history'),
    path('detailsession/<int:session_id>/', get_workout_by_session, name='get_workout_by_session'),
    path('widjetrecords/<str:device_id>/', ExerciseWidjetRecordsView.as_view(), name='exercise-records'),
    path('api/payment/', create_charge, name='make_payment'),
    path('payment/result/', payment_result, name='payment_result'),
    path('payment/post_result/', post_payment_result, name='post_payment_result'),
    path('workouts/<int:pk>/delete/', delete_workout, name='delete_workout'),
]
