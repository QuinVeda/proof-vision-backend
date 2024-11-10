from django.db import models

# Create your models here.


def upload_path(instance, filename):
    filename = filename.replace(" ", "_").lower()
    return f"detections/{instance.user.id}/{filename}"


class Detection(models.Model):
    TYPES = (
        ("audio", "Audio"),
        ("video", "Video"),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPES)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=upload_path)
    results = models.JSONField(blank=True, null=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.type == "video":
            if not self.file.name.endswith(".mp4"):
                raise ValueError("File must be a .mp4")
        elif self.type == "audio":
            if not self.file.name.endswith(".mp3"):
                raise ValueError("File must be a .mp3")
        super().save(*args, **kwargs)
