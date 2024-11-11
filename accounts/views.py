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
