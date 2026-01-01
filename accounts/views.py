from django.shortcuts import render
from django.http import JsonResponse
import base64, json

def debug_claims(request):
    raw = request.META.get('X-MS-CLIENT-PRINCIPAL')
    if raw:
        decoded = base64.b64decode(raw).decode('utf-8')
        return JsonResponse(json.loads(decoded), safe=False)
    return JsonResponse({'error': 'No principal found'})

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

