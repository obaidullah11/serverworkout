# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse, HttpResponse
# import json
# import uuid
# from Crypto.Cipher import AES
# import base64
# from .models import KnetTransaction
# from datetime import datetime


# def generate_track_id():
#     """
#     Generate a unique track ID for each transaction.
#     """
#     track_id = str(uuid.uuid4())[:8]
#     print(f"Generated Track ID: {track_id}")
#     return track_id


# class KnetPayment:
#     TRANPORTAL_ID = "540801"
#     TRANPORTAL_PASSWORD = "540801pg"
#     TERMINAL_RESOURCE_KEY = "9D2JJ07HA1Y47RF3"
#     # Correct test URL for RAW method
#     TEST_URL = "https://kpaytest.com.kw/kpg/PaymentHTTP.htm"

#     def encrypt_AES(self, data):
#         try:
#             key = self.TERMINAL_RESOURCE_KEY.encode('utf-8')
#             cipher = AES.new(key, AES.MODE_CBC, key)
#             pad_length = 16 - (len(data) % 16)
#             padded_data = data + (chr(pad_length) * pad_length)
#             encrypted = cipher.encrypt(padded_data.encode('utf-8'))
#             return base64.b64encode(encrypted).decode('utf-8')
#         except Exception as e:
#             print(f"Encryption error: {str(e)}")
#             raise


# @csrf_exempt
# def initiate_payment(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             amount = "{:.3f}".format(float(data.get('amount', '0')))
#             track_id = generate_track_id()

#             knet = KnetPayment()
            
#             # Build absolute URLs
#             response_url = 'https://mfarhanakram.eu.pythonanywhere.com/payment/response/'
#             error_url = 'https://mfarhanakram.eu.pythonanywhere.com/payment/error/'

#             # Build request string in correct order
#             request_string = (
#                 # f"id={knet.TRANPORTAL_ID}"
#                 f"amt={amount}&"
#                 f"action=1&"
#                 f"responseURL={response_url}&"
#                 f"errorURL={error_url}&"
#                 f"trackid={track_id}&"
#                 f"udf1=test1&"
#                 f"udf2=test2&"
#                 f"udf3=test3&"
#                 f"udf4=test4&"
#                 f"udf5=test5&"
#                 f"currencycode=414&"
#                 f"langid=USA&"
#                 f"id={knet.TRANPORTAL_ID}&"
#                 f"password={knet.TRANPORTAL_PASSWORD}"
#                 f"errorURL={error_url}&"
#                 f"responseURL={response_url}&"
#             )

#             # Encrypt the request
#             encrypted_data = knet.encrypt_AES(request_string)

#             # Build payment URL - simplified for direct redirect
#             # payment_url = (
#             #     f"{knet.TEST_URL}?"
#             #     f"param=paymentInit&"
#             #     f"trandata={encrypted_data}"
#             #     f"tranportalId={knet.TRANPORTAL_ID}"
#             # )
#             payment_url = (
#                 f"{knet.TEST_URL}?"
#                 f"param=paymentInit&"
#                 f"trandata={encrypted_data}&"
#                 f"errorURL={error_url}&"
#                 f"responseURL={response_url}&"
#                 f"tranportalId={knet.TRANPORTAL_ID}"
#             )

#             # Store initial transaction
#             transaction = KnetTransaction.objects.create(
#                 track_id=track_id,
#                 amount=amount,
#                 status='INITIATED'
#             )

#             # Return URL for redirect
#             return JsonResponse({
#                 'success': True,
#                 'payment_url': payment_url,
#                 'track_id': track_id
#             })

#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             }, status=400)

#     return JsonResponse({
#         'success': False,
#         'error': 'Method not allowed'
#     }, status=405)
# @csrf_exempt
# def payment_response(request):
#     """
#     Handles the notification from KNET (server-to-server)
#     """
#     try:
#         # Get the encrypted response from the output stream
#         trandata = request.POST.get('trandata')
        
#         if trandata:
#             knet = KnetPayment()
#             decrypted_data = knet.decrypt_AES(trandata)
            
#             # Parse the response
#             params = dict(item.split('=') for item in decrypted_data.split('&'))
            
#             # Get track_id from response
#             track_id = params.get('trackid')
            
#             # Update transaction in database
#             transaction = KnetTransaction.objects.filter(track_id=track_id).first()
#             if transaction:
#                 transaction.result = params.get('result')
#                 transaction.payment_id = params.get('paymentid')
#                 transaction.auth = params.get('auth')
#                 transaction.ref = params.get('ref')
#                 transaction.tran_id = params.get('tranid')
#                 transaction.encrypted_response = trandata
#                 transaction.decrypted_response = decrypted_data
#                 transaction.save()

#             # Generate receipt URL
#             receipt_url = request.build_absolute_uri(
#                 f'/payment/receipt/{track_id}/'
#             )

#             # Return REDIRECT as required
#             return HttpResponse(f"REDIRECT={receipt_url}")
            
#         return HttpResponse("No transaction data received", status=400)

#     except Exception as e:
#         print(f"Payment response error: {str(e)}")
#         return HttpResponse("Error processing payment", status=500)
        
        
# @csrf_exempt
# def payment_error(request):
#     """
#     Handles KNET payment errors and returns JSON response
#     """
#     try:
#         # Get error parameters
#         error_code = request.GET.get('Error', '')
#         error_text = request.GET.get('ErrorText', '')
#         track_id = request.GET.get('trackid', '')

#         # Update transaction if track_id exists
#         if track_id:
#             transaction = KnetTransaction.objects.filter(track_id=track_id).first()
#             if transaction:
#                 transaction.result = 'ERROR'
#                 transaction.error_code = error_code
#                 transaction.error_text = error_text
#                 transaction.save()

#         # Return JSON response
#         return JsonResponse({
#             'status': 'error',
#             'error_code': error_code,
#             'error_text': error_text,
#             'track_id': track_id,
#             'timestamp': datetime.now().isoformat(),
#             'debug': {
#                 'query_params': dict(request.GET.items()),
#                 'headers': dict(request.headers)
#             }
#         }, status=400)

#     except Exception as e:
#         # Return system error
#         return JsonResponse({
#             'status': 'error',
#             'error_code': 'SYSTEM_ERROR',
#             'error_text': str(e),
#             'timestamp': datetime.now().isoformat()
#         }, status=500)




from django.urls import path
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import json

# Configuration
KNET_TRANSPORTAL_ID = "540801"
KNET_TRANSPORTAL_PASSWORD = "540801pg"
KNET_TERMINAL_RESOURCE_KEY = "9D2JJ07HA1Y47RF3"
KNET_TEST_URL = "https://kpaytest.com.kw/kpg/PaymentHTTP.htm"

class KNET:
    def __init__(self):
        self.config = {
            "TRANSPORTAL_ID": KNET_TRANSPORTAL_ID,
            "TRANSPORTAL_PASSWORD": KNET_TRANSPORTAL_PASSWORD,
            "TERMINAL_RESOURCE_KEY": KNET_TERMINAL_RESOURCE_KEY,
            "TERMINAL_URI": KNET_TEST_URL,
        }
        print(f"KNET initialized with config: {self.config}")

    def create_payment(self, amount, language="ENG", user_vars=None):
        print(f"Creating payment with amount: {amount}, language: {language}, user_vars: {user_vars}")
        payload = {
            "id": self.config["TRANSPORTAL_ID"],
            "password": self.config["TRANSPORTAL_PASSWORD"],
            "amt": amount,
            "langid": language,
            "currencycode": "414",
            "action": "1",
            **(user_vars or {}),
        }
        encrypted_payload = self._encrypt_payload(payload)
        print(f"Encrypted payload: {encrypted_payload}")
        response = requests.post(self.config["TERMINAL_URI"], data={"param": encrypted_payload})
        print(f"Response status code: {response.status_code}, Response body: {response.text}")
        return self._decrypt_response(response)

    def _encrypt_payload(self, data):
        key = self.config["TERMINAL_RESOURCE_KEY"].encode()
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()
        json_data = json.dumps(data).encode()
        padded_data = json_data + b"\0" * (16 - len(json_data) % 16)
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted).decode()

    def _decrypt_response(self, response):
        try:
            key = self.config["TERMINAL_RESOURCE_KEY"].encode()
            cipher = Cipher(algorithms.AES(key), modes.ECB())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(base64.b64decode(response.text)) + decryptor.finalize()
            result = json.loads(decrypted.strip(b"\0").decode())
            print(f"Decrypted response: {result}")
            return result
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return {"STATUS": "error", "DESCRIPTION": str(e)}

# Views
@csrf_exempt
@require_POST
def create_payment_api(request):
    try:
        data = json.loads(request.body)  # Parse the incoming JSON data
        print(f"Request data: {data}")  # Log the incoming data
        
        amount = data.get("amount")  # Extract amount from the parsed data
        if amount is None:
            return JsonResponse({"STATUS": "error", "DESCRIPTION": "Missing amount in request."})

        language = data.get("language", "ENG")
        user_vars = {
            "trackid": data.get("trackid"),
            "udf1": data.get("udf1"),
            "udf2": data.get("udf2"),
            "udf3": data.get("udf3"),
            "udf4": data.get("udf4"),
        }
        
        knet = KNET()  # Create an instance of the KNET class
        response = knet.create_payment(amount, language, user_vars)  # Call the method to create payment
        
        print(f"Response from KNET: {response}")  # Log the response from KNET
        
        return JsonResponse(response)  # Return the response as JSON
    except Exception as e:
        print(f"Error in create_payment_api: {str(e)}")  # Log any error
        return JsonResponse({"STATUS": "error", "DESCRIPTION": str(e)})  # Return error as JSON


@csrf_exempt
@require_POST
def listen_payment_api(request):
    try:
        print("Listening for payment...")
        knet = KNET()
        decrypted_data = knet._decrypt_response(request)
        print(f"Decrypted data from payment listener: {decrypted_data}")
        return JsonResponse({"STATUS": "success", "DATA": decrypted_data})
    except Exception as e:
        print(f"Error in listen_payment_api: {str(e)}")
        return JsonResponse({"STATUS": "error", "DESCRIPTION": str(e)})

def complete_payment_api(request):
    tracking_id = request.GET.get("TRACKING_ID", "")
    status = request.GET.get("STATUS", "error")
    print(f"Completing payment with TRACKING_ID: {tracking_id}, STATUS: {status}")
    return JsonResponse({"TRACKING_ID": tracking_id, "STATUS": status})













