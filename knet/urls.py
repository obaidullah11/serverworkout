from django.urls import path
# from .views import initiate_payment, payment_response, payment_error
from .views import *
# urlpatterns = [
#     path('payment/initiate/', initiate_payment, name='initiate_payment'),
#     path('payment/response/', payment_response, name='payment_response'),
#     path('payment/error/', payment_error, name='payment_error'),
# ]
# URL Patterns
urlpatterns = [
    path("api/knet/create/", create_payment_api, name="create_payment_api"),
    path("api/knet/listen/", listen_payment_api, name="listen_payment_api"),
    path("api/knet/complete/", complete_payment_api, name="complete_payment_api"),
]