from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create-token/', create_token, name='create_token'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




