from .models import Detection
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from proofvision.services import AmazonLambdaService


class DetectionSerializer(ModelSerializer):

    class Meta:
        model = Detection
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def validate(self, attrs):
        if attrs["type"] == "video":
            if not attrs["file"].name.endswith(".mp4"):
                raise ValidationError({"file": "File must be a .mp4"})
        elif attrs["type"] == "audio":
            if not attrs["file"].name.endswith(".mp3"):
                raise ValidationError({"file": "File must be a .mp3"})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        instance = super().create(validated_data)
        data = {"id": instance.id, "type": instance.type, "file": instance.file.url}
        AmazonLambdaService().start(data)
        return instance
