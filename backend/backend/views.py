from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

def home(request):
  return render(request, 'home.html')

class ProtectedView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    return Response({'message': 'This is a protected view'})
