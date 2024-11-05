from dj_rest_auth.registration.urls import urlpatterns as dj_rest_auth_registration_urls
from dj_rest_auth.urls import urlpatterns as dj_rest_auth_urls
from rest_framework.routers import DefaultRouter
from collections import OrderedDict
from django.conf import settings
import copy

class APIRouter(DefaultRouter):
    include_root_view = settings.DEBUG
    dj_rest_urls = dj_rest_auth_urls + dj_rest_auth_registration_urls
    auth_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_auth_urls()

    def get_api_root_view(self, api_urls=None):
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name

        if self.auth_urls == []:
            self.get_auth_urls()

        for url in self.auth_urls:
            api_root_dict[url.name] = url.name

        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)

    def get_urls(self):
        urls = super().get_urls()
        return urls + self.auth_urls

    def get_auth_urls(self):
        for url in self.dj_rest_urls:
            if url.name.startswith("account"):
                continue

            url.name = url.name.replace("_", "-")
            url.pattern._route = f"auth/{url.pattern._route}"

            if url.name.startswith("rest"):
                url.name = url.name.replace("rest-", "")

            if url.name == "register":
                url.pattern._route = "auth/register/"

            if url.name == "password-reset-confirm":
                reset_url = copy.deepcopy(url)
                reset_url.name = "password_reset_confirm"
                reset_url.pattern._route = (
                    "auth/password/reset/confirm/<str:uid>/<str:token>"
                )
                self.auth_urls.append(reset_url)

            self.auth_urls.append(url)


# Register your viewsets here
router = APIRouter()
