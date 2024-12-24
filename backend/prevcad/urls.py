from rest_framework import routers
from django.urls import path, include
from prevcad.models import HealthCategory

from prevcad.views.profiles import getProfile, uploadProfileImage
from prevcad.views.text_recomendations import TextRecomendationsView
from prevcad.views.health_categories import HealthCategoryListView, save_evaluation_responses, create_health_category
from django.conf import settings
from django.conf.urls.static import static
from .views import admin_views


router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/text_recommendations/', TextRecomendationsView, basename='text_recommendations')



# Rutas de la API
urlpatterns = [
  path('', include(router.urls)),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
  path('prevcad/user/profile/upload_image/', uploadProfileImage, name='upload_profile_image'),
  path('prevcad/health_categories/', HealthCategoryListView.as_view(), name='health-categories'),
  path('prevcad/health-categories/<int:category_id>/responses/', save_evaluation_responses, name='save_responses'),
 
  path('prevcad/health-categories/create', 
       create_health_category, 
       name='create_health_category'),
  path('admin/update-evaluation-form/<int:template_id>/', admin_views.update_evaluation_form, name='update_evaluation_form'),
  path('admin/update-training-form/<int:template_id>/', admin_views.update_training_form, name='update_training_form'),
]