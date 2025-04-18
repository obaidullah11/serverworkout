from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

 # Import your routing configuration for WebSocket connections

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('users.urls')),
    path('', include('train.urls')),
    path('', include('workout.urls')),
    # path('', include('knet.urls')),
    # path('', include('token_scheduling.urls')),
    # path('', include('notifications.urls')),

    # Add path for WebSocket connections

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
