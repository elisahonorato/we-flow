from django.contrib import admin
from .category_template import CategoryTemplateAdmin
from .health_category import HealthCategoryAdmin
from .encoders import CustomJSONEncoder
from ..models import CategoryTemplate, HealthCategory
from .filters import HealthStatusFilter

from .appointment import AppointmentAdmin
from .user import CustomUserAdmin