from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import UserToken
import json
from django.utils.timezone import localtime

@csrf_exempt
def create_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_name = data.get('user_name')
        description = data.get('description')

        if not user_name or not description:
            return JsonResponse({"success": False, "message": "Invalid input"}, status=400)

        new_user = UserToken.assign_token(user_name, description)

        # Convert to local time (Pakistan Standard Time due to settings)
        local_time = localtime(new_user.assigned_time)

        # Format the time
        formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')

        return JsonResponse({
            "success": True,
            "token": new_user.token,
            "assigned_time": formatted_time
        }, status=201)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
