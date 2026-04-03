import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser


def register_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "worker")

    if not email or not username or not password:
        return JsonResponse({"error": "Missing fields"}, status=400)

    if CustomUser.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email exists"}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username exists"}, status=400)

    CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role
    )

    return JsonResponse({"message": "User created"}, status=201)


def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)

    identifier = data.get("identifier")  # email yoki username
    password = data.get("password")

    if not identifier or not password:
        return JsonResponse({"error": "Missing fields"}, status=400)

    # 🔍 Userni topamiz
    user = None
    if "@" in identifier:
        user = CustomUser.objects.filter(email=identifier).first()
    else:
        user = CustomUser.objects.filter(username=identifier).first()

    if user:
        # ⚠️ MUHIM: authenticate username bilan ishlaydi
        user = authenticate(request, username=user.username, password=password)

        if user:
            login(request, user)
            return JsonResponse({"message": "Login success"})

    return JsonResponse({"error": "Invalid credentials"}, status=400)


def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    logout(request)
    return JsonResponse({"message": "Logged out"})