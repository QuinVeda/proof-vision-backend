from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import User


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"{settings.FRONTEND_CONFIRM_EMAIL_URL}?key={emailconfirmation.key}"

    def respond_email_verification_sent(self, request, user):
        return

    def format_email_subject(self, subject):
        return subject

    def confirm_email(self, request, email_address):
        is_confirmed = super().confirm_email(request, email_address)
        if is_confirmed:
            request.user = email_address.user
            context = {"site_name": get_current_site(request).name, "request": request}
            self.send_mail(
                "account/email/email_registered", email_address.user.email, context
            )
        return is_confirmed

    def send_mail(self, template_prefix, email, context):
        if "activate_url" in context:
            context["activate_url"] = (
                f"{settings.FRONTEND_CONFIRM_EMAIL_URL}?key={context['key']}"
            )

        if "password_reset_url" in context:
            uid = context["password_reset_url"].split("/")[-2]
            token = context["password_reset_url"].split("/")[-1]
            context["password_reset_url"] = (
                f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}"
            )

        if "request" in context:
            context["current_site"] = get_current_site(context["request"])
            context["user"] = context["request"].user
            if context["request"].user.is_anonymous:
                context["user"] = "User"
            email = context["request"].data.get("email", None)
            if email:
                context["user"] = email
                user = User.objects.filter(email=email)
                if user.exists():
                    context["user"] = user.first()

        context["support_email"] = settings.SUPPORT_EMAIL
        msg = self.render_mail(template_prefix, email, context)

        if "attachment" in context:
            filename = context["attachment"]["name"]
            data = context["attachment"]["data"]
            type = context["attachment"]["content_type"]
            msg.attach(filename, data, type)

        msg.send()
