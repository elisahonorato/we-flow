import re
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.text import Truncator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import json
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from .models import (
  TextRecomendation,
  Profile,
  CategoryTemplate,
  HealthCategory,
  ActivityNode,
  ActivityNodeDescription,
  TextQuestion,
  SingleChoiceQuestion,
  MultipleChoiceQuestion,
  ScaleQuestion,
  ImageQuestion,
  ResultNode,
  WeeklyRecipeNode
)

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'Profiles'
  fk_name = 'user'

# Add HealthCategory inline to show categories in user admin
class HealthCategoryInline(admin.TabularInline):
  model = HealthCategory
  extra = 0  # Don't show empty forms
  readonly_fields = ['template']  # Make them read-only
  can_delete = True
  verbose_name_plural = 'Health Categories'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
  inlines = [ProfileInline, HealthCategoryInline]  # Add HealthCategoryInline
  list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
  list_filter = ('is_staff', 'is_superuser', 'is_active')

  def get_inline_instances(self, request, obj=None):
    if not obj:
      return list()
    return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
  change_form_template = 'admin/categorytemplate/change_activity_form.html'
  list_display = ('name', 'is_active', 'preview_icon', 'description_preview')
  list_filter = ('is_active',)
  search_fields = ('name', 'description')

  
  
  fieldsets = (
    ('Información Básica', {
      'fields': ('name', 'description', 'icon', 'is_active')
    }),
    ('Formulario de Evaluación', {
      'classes': ('wide',),
      'fields': ('evaluation_form_button',),
      'description': 'Configure las preguntas del formulario de evaluación.'
    }),
    ('Nodos de Entrenamiento', {
      'classes': ('collapse',),
      'fields': ('training_nodes_button',),
    }),
  )
  readonly_fields = ('evaluation_form_button', 'training_nodes_button')

  def preview_icon(self, obj):
    if obj.icon:
      return format_html('<img src="{}" style="height: 30px; width: auto;"/>', obj.icon.url)
    return "Sin ícono"
  preview_icon.short_description = 'Ícono'

  def description_preview(self, obj):
    return Truncator(obj.description).chars(50)
  description_preview.short_description = 'Descripción'

  def evaluation_form_button(self, obj):
    return mark_safe(f"""
  <div class="form-row field-evaluation_form">
    <label for="id_evaluation_form">Formulario de Evaluación</label>
    <button type="button" class="btn btn-primary" onclick="openViewFormModal({obj.id})">
      Ver Formulario
    </button>
  </div>
    """)
  

  evaluation_form_button.short_description = "Formulario de Evaluación"

  def training_nodes_button(self, obj):
    return mark_safe(f"""
      <button type="button" class="btn btn-primary" onclick="openTrainingFormModal({obj.id})">
        Ver Nodos de Entrenamiento
      </button>
    """)
  training_nodes_button.short_description = "Nodos de Entrenamiento"

  def response_change(self, request, obj):
      if "_add_node" in request.POST:
          node_data = self._get_node_data_from_request(request)
          obj.add_activity_node(node_data)
          self.message_user(request, "Pregunta agregada exitosamente")
      elif "_edit_node" in request.POST:
          node_id = request.POST.get('node_id')
          node_data = self._get_node_data_from_request(request)
          self._edit_node(obj, node_id, node_data)
          self.message_user(request, "Pregunta actualizada exitosamente")
      elif "_delete_node" in request.POST:
          node_id = request.POST.get('node_id')
          self._delete_node(obj, node_id)
          self.message_user(request, "Pregunta eliminada exitosamente")
      return super().response_change(request, obj)

  def formatted_description(self, obj):
    truncated_text = Truncator(obj.description).chars(50, truncate='...')
    return format_html(
      f'<span title="{obj.description}">{truncated_text}</span>'
    )

  formatted_description.short_description = "Descripción"
  
  

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models

class HealthStatusFilter(SimpleListFilter):
    title = 'Estado'
    parameter_name = 'status_color'

    def lookups(self, request, model_admin):
        return HealthCategory.COLOR_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_color=self.value())

@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'user_info', 
        'template_info', 
        'status_badge', 
        'completion_status',
        'date_display'
    )
    readonly_fields = ['get_detailed_responses', 'completion_date']
    list_filter = (
        HealthStatusFilter, 
        'template',
        ('user', admin.RelatedOnlyFieldListFilter),
        'completion_date'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('template', 'completion_date')
        }),
        ('Respuestas', {
            'fields': ('get_detailed_responses',),
            'classes': ('collapse',)
        }),
    )
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    def user_info(self, obj):
        return format_html(
            '<div class="flex-cell" style="min-width:100px; flex: 1;">'
            '<strong>{}</strong>'
            '</div>',
            obj.user.username
        )
    user_info.short_description = "Usuario"

    def template_info(self, obj):
        if obj.template:
            return format_html(
                '<div class="flex-cell" style="min-width:120px; flex: 1.5;">'
                '<strong>{}</strong><br/>'
                '<small style="color: #666">{}</small>'
                '</div>',
                obj.template.name,
                Truncator(obj.template.description).chars(25)
            )
    template_info.short_description = 'Categoría'


    def status_badge(self, obj):
        colors = {
            'green': ('#28a745', '✓'),
            'yellow': ('#ffc107', '!'),
            'red': ('#dc3545', '×'),
        }
        if obj.status_color:
            color, symbol = colors.get(obj.status_color, ('#6c757d', '-'))
            return format_html(
                '<div class="flex-cell" style="flex: 0.5; text-align: center;">'
                '<span style="'
                'background-color: {};'
                'color: white;'
                'padding: 1px 6px;'
                'border-radius: 10px;'
                'display: inline-block;'
                '">{}</span>'
                '</div>',
                color, symbol
            )
        return '-'
    status_badge.short_description = 'Estado'

    def completion_status(self, obj):
        return format_html(
            '<div class="flex-cell" style="flex: 0.5; text-align: center;">'
            '<span style="color: {}">{}</span>'
            '</div>',
            '#28a745' if obj.completion_date else '#dc3545',
            '✓' if obj.completion_date else '×'
        )
    completion_status.short_description = 'Completado'

    def date_display(self, obj):
        if obj.completion_date:
            return format_html(
                '<div class="flex-cell" style="flex: 1; text-align: right;">'
                '<small style="color: #666">{}</small>'
                '</div>',
                obj.completion_date.strftime('%d/%m/%Y')
            )
        return ''
    date_display.short_description = 'Fecha'

    def get_response_summary(self, obj):
        if not obj.responses:
            return "Sin respuestas"
        return f"{len(obj.responses)} respuestas registradas"
    get_response_summary.short_description = "Respuestas"

    def get_detailed_responses(self, obj):
        if not obj.responses:
            return "No hay respuestas registradas"

        html = ["""
            <table style='width:100%; border-collapse: collapse; margin-top: 10px;'>
                <tr>
                    <th style='border:1px solid #ddd; padding:12px; background-color:#f8f9fa;'>ID</th>
                    <th style='border:1px solid #ddd; padding:12px; background-color:#f8f9fa;'>Tipo</th>
                    <th style='border:1px solid #ddd; padding:12px; background-color:#f8f9fa;'>Pregunta</th>
                    <th style='border:1px solid #ddd; padding:12px; background-color:#f8f9fa;'>Respuesta</th>
                    <th style='border:1px solid #ddd; padding:12px; background-color:#f8f9fa;'>Fecha</th>
                </tr>
        """]

        for node_id, response_data in obj.responses.items():
            try:
                # Extraer datos del nuevo formato de respuesta
                question = response_data.get('question', 'Sin pregunta')
                response_type = response_data.get('type', 'Desconocido')
                answer_data = response_data.get('answer', {})
                timestamp = response_data.get('metadata', {}).get('timestamp', '')
                
                # Formatear la respuesta según el tipo
                formatted_answer = ""
                if response_type == 'SINGLE_CHOICE_QUESTION':
                    selected_idx = answer_data.get('selectedOption')
                    options = answer_data.get('options', [])
                    formatted_answer = options[selected_idx] if selected_idx is not None and options else "No seleccionada"
                
                elif response_type == 'MULTIPLE_CHOICE_QUESTION':
                    selected_indices = answer_data.get('selectedOptions', [])
                    options = answer_data.get('options', [])
                    selected_options = [options[i] for i in selected_indices if i < len(options)]
                    formatted_answer = ", ".join(selected_options) if selected_options else "No seleccionada"
                
                elif response_type == 'TEXT_QUESTION':
                    formatted_answer = answer_data.get('text', 'Sin respuesta')

                # Formatear la fecha
                formatted_date = timestamp.split('T')[0] if timestamp else ''

                html.append(f"""
                    <tr>
                        <td style='border:1px solid #ddd; padding:8px;'>{response_data.get('id', node_id)}</td>
                        <td style='border:1px solid #ddd; padding:8px;'>{response_type}</td>
                        <td style='border:1px solid #ddd; padding:8px;'>{question}</td>
                        <td style='border:1px solid #ddd; padding:8px;'>{formatted_answer}</td>
                        <td style='border:1px solid #ddd; padding:8px;'>{formatted_date}</td>
                    </tr>
                """)
                
            except Exception as e:
                print(f"Error processing response {node_id}: {str(e)}")
                html.append(f"""
                    <tr>
                        <td style='border:1px solid #ddd; padding:8px;'>{node_id}</td>
                        <td colspan="4" style='border:1px solid #ddd; padding:8px; color: red;'>
                            Error procesando respuesta: {str(e)}
                        </td>
                    </tr>
                """)

        html.append("</table>")
        return mark_safe(''.join(html))
    get_detailed_responses.short_description = "Detalle de Respuestas"

@admin.register(TextRecomendation)
class TextRecomendationAdmin(admin.ModelAdmin):
    list_display = ('theme', 'category', 'sub_category')
    list_filter = ('theme', 'category', 'sub_category')
    search_fields = ('theme', 'category', 'sub_category', 'learn', 'remember', 'data', 'context_explanation')
    ordering = ('theme', 'category')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('theme', 'category', 'sub_category')
        }),
        ('Contenido', {
            'fields': ('learn', 'remember', 'data', 'practic_data', 'context_explanation'),
            'classes': ('wide',)
        }),
        ('Metadatos', {
            'fields': ('quote_link', 'keywords'),
            'classes': ('collapse',),
            'description': 'Información adicional'
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

