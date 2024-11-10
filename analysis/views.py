import json
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Detection
from .serializers import DetectionSerializer

# Create your views here.


class DetectionViewSet(ModelViewSet):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]
    search_fields = ["name"]
    filterset_fields = ["type"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Detection.objects.filter(user=self.request.user)

    @action(
        detail=False,
        methods=["post"],
        url_path="result",
        url_name="Detection Results",
        permission_classes=[AllowAny],
    )
    def results(self, request, *args, **kwargs):
        body = json.loads(request.body)
        data = body["data"]
        detection = Detection.objects.get(id=data["id"])
        detection.results = data["results"]
        detection.save()
        serializer = DetectionSerializer(detection)
        data = {
            "message": "Results updated successfully",
            "data": serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)
