from rest_framework import viewsets, status
from rest_framework.response import Response
from prevcad.models import HealthCategory, TextRecomendation
from prevcad.serializers import HealthCategorySerializer, TextRecomendationSerializer

class HealthCategoryView(viewsets.ModelViewSet):
    queryset = HealthCategory.objects.all()
    serializer_class = HealthCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TextRecomendationsView(viewsets.ModelViewSet):
    queryset = TextRecomendation.objects.all()
    serializer_class = TextRecomendationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except TextRecomendation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
