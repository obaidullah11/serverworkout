from django.urls import path
from django.conf import settings
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    # Exercise URLs
    path('getallcategory/', get_all_categories, name='get_all_categories'),
    path('exercises/', exercise_list_create, name='exercise-list-create'),
    path('exercises/<int:pk>/', exercise_detail, name='exercise-detail'),
    path('api/body-parts/', BodyPartListView.as_view(), name='body-part-list'),
    path('api/exercises/', FilteredExerciseListView.as_view(), name='filtered-exercise-list'),
    path('api/exercise/update/<int:pk>/', ExerciseUpdateView.as_view(), name='exercise-update'),
    # # Routine URLs
    # path('routines/', routine_list_create, name='routine-list-create'),
    # path('routines/<int:pk>/', routine_detail, name='routine-detail'),
    # path('routines/client/<int:client_id>/', routine_by_client, name='routine-by-client'),
    path('api/exercises/<str:device_id>/', get_exercises_by_device_id, name='exercise-list-by-device-id'),
    # # Session URLs
    # path('sessions/', session_list_create, name='session-list-create'),
    # path('sessions/<int:pk>/', session_detail, name='session-detail'),
    # path('user/sessions/<int:user_id>/', user_sessions, name='session-detail'),
    path('api/exercises/v3/<str:device_id>/', get_exercises_by_device_id_pagination, name='get_exercises_by_device_id_pagination'),


    # # Setgroup URLs

    # path('setgroups/<int:pk>/',setgroup_detail, name='setgroup-detail'),

    # # Set URLs
    # path('sets/', set_list_create, name='set-list-create'),
    # path('sets/<int:pk>/', set_detail, name='set-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
