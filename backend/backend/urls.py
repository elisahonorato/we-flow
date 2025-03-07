"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import home
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_simplejwt.views import (
  TokenObtainPairView,
  TokenRefreshView,
  TokenVerifyView
)

from prevcad.views.admin_views import update_training_form, delete_training_node

urlpatterns = [
  path('', home, name='home'),
  path('admin/', admin.site.urls),
  path('api/', include('prevcad.urls')),
  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
  path('api/admin/categorytemplate/<int:template_id>/delete_node/<str:node_id>/', 
       delete_training_node, 
       name='delete_training_node'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
