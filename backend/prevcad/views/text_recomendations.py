from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from prevcad.models import (
  TextRecomendation,
)
from prevcad.serializers.text_recomendation_serializer import (
  TextRecomendationSerializer,
)


class TextRecomendationsView(viewsets.ModelViewSet):
  queryset = TextRecomendation.objects.all()
  serializer_class = TextRecomendationSerializer

  def create(self, request: Request, *args, **kwargs) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  def retrieve(self, request: Request, pk=None, *args, **kwargs) -> Response:
    try:
      instance = self.get_object()
      serializer = self.get_serializer(instance)
      return Response(serializer.data)
    except TextRecomendation.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)

  def list(self, request, *args, **kwargs) -> Response:
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)
