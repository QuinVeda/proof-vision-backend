from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator
from rest_framework import serializers, exceptions
from accounts.models import User


class RegisterSerializer(RegisterSerializer):
    username = None
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def custom_signup(self, request, user):
        name = self.validated_data.get("name", "")
        user.name = name
        user.save()


class LoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except serializers.ValidationError as e:
            raise exceptions.AuthenticationFailed(str(e.detail[0]))


class UserDetailSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ("id", "email", "name", "phone_number")
