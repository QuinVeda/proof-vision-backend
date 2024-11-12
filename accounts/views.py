from django.shortcuts import render
import requests

# Create your views here.


def verify_email(request):
    key = request.GET.get("key", None)
    if key:
        url = f"https://{request.get_host()}/api/auth/verify-email/"
        res = requests.post(url, data={"key": key})
        if res.status_code == 200:
            return render(
                request,
                "account/verify_email.html",
                {"message": "Email verified successfully"},
            )
    return render(request, "account/verify_email.html")

def reset_password(request):
    uid = request.GET.get("uid", None)
    token = request.GET.get("token", None)

    if request.method == "POST":
        uid = request.POST.get("uid", None)
        token = request.POST.get("token", None)
        passwd1 = request.POST.get("passwd1", None)
        passwd2 = request.POST.get("passwd2", None)
        if passwd1 and passwd2 and passwd1 != passwd2:
            return render(
                request,
                "account/reset_password.html",
                {"message": "Passwords do not match"},
            )
        url = f"https://{request.get_host()}/api/auth/password/reset/confirm/"
        res = requests.post(url, data={"uid": uid, "token": token, "new_password1": passwd1, "new_password2": passwd2})
        if res.status_code == 200:
            return render(
                request,
                "account/reset_password.html",
                {"message": "Password reset successfully"},
            )
        return render(request, "account/reset_password.html", {"message": "Error resetting password."})
    return render(request, "account/reset_password.html", {"uid": uid, "token": token})
