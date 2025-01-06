from rest_framework import serializers
from prevcad.models import HealthCategory, CategoryTemplate

class HealthCategorySerializer(serializers.ModelSerializer):
    # Campos básicos
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    
    # Campos de evaluación
    evaluation_type = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
 
    
    # Campos de estado y recomendaciones
    status = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    
    # Campos adicionales
    training_form = serializers.SerializerMethodField()

    STATUS_COLORS = {
        'verde': {'color': '#008000', 'text': 'No Riesgoso'},
        'amarillo': {'color': '#FFFF00', 'text': 'Poco Riesgoso'},
        'rojo': {'color': '#FF0000', 'text': 'Riesgoso'},
        'gris': {'color': '#808080', 'text': 'Neutral'},
    }

    class Meta:
        model = HealthCategory
        fields = [
            'id',
            'name',
            'icon',
            'description',
            'evaluation_type',
            'evaluation_form',
          
            'status',
            'recommendations',
            'training_form',
          
       
        
        ]

    def get_template_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos del template de forma segura"""
        return getattr(obj.template, attr, default) if obj.template else default

    def get_evaluation_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos del evaluation_form de forma segura"""
        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            return getattr(evaluation_form, attr, default)
        except Exception as e:
            print(f"Error getting evaluation attribute {attr}: {str(e)}")
            return default

    def get_recommendation_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos de recommendation de forma segura"""
        try:
            recommendation = obj.get_or_create_recommendation()
            return getattr(recommendation, attr, default)
        except Exception as e:
            print(f"Error getting recommendation attribute {attr}: {str(e)}")
            return default

    # Getters básicos
    def get_name(self, obj):
        return self.get_template_attribute(obj, 'name')

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            return obj.template.get_icon_base64()
        return None

    def get_description(self, obj):
        return (self.get_template_attribute(obj, 'root_node.description') or 
                self.get_template_attribute(obj, 'description'))

    def get_evaluation_type(self, obj):
        eval_type = self.get_template_attribute(obj, 'evaluation_type')
        if not eval_type:
            return None
            
        types = {
            'SELF': 'Autoevaluación',
            'PROFESSIONAL': 'Evaluación Profesional'
        }
        return {
            'type': eval_type,
            'label': types.get(eval_type, 'Desconocido')
        }


    def get_evaluation_form(self, obj):
        eval_form = obj.get_or_create_evaluation_form()
        if eval_form:
            # Debug
            print("Procesando evaluation_form para:", obj.template.name if obj.template else "No template")
            
            template = obj.template
            question_nodes = []
            
            if template:
                # Debug
                print("Tipo de evaluación:", template.evaluation_type)
                
                
                # Si es evaluación profesional
                if template.evaluation_type == 'PROFESSIONAL':
                    question_nodes = [
                        {
                            'id': 'observations',
                            'type': 'text',
                            'label': 'Observaciones',
                            'required': True
                        },
                        {
                            'id': 'diagnosis',
                            'type': 'text',
                            'label': 'Diagnóstico',
                            'required': True
                        }
                    ]
                    print("Nodos profesionales creados:", question_nodes)  # Debug
                # Si es autoevaluación
                else:
                    try:
                        # Obtener los nodos del template
                        if hasattr(template, 'get_question_nodes'):
                            question_nodes = template.get_question_nodes()
                         
                        else:
                            print("El template no tiene método get_question_nodes")  # Debug
                            # Intentar obtener nodos del root_node
                            if hasattr(template, 'root_node') and template.root_node:
                                question_nodes = [
                                    {
                                        'id': node.id,
                                        'type': node.type,
                                        'label': node.text,
                                        'required': getattr(node, 'required', False),
                                        'options': getattr(node, 'options', None)
                                    }
                                    for node in template.root_node.get_descendants()
                                    if node.type == 'QUESTION'
                                ]
                                print("Nodos obtenidos del root_node:", question_nodes)  # Debug
                    except Exception as e:
                        print("Error obteniendo nodos:", str(e))  # Debug
                        question_nodes = []
            
            # Debug final
            print("Nodos finales a devolver:", question_nodes)
            
            return {
                'completed_date': eval_form.completed_date,
                'responses': eval_form.responses,
                'professional_responses': eval_form.professional_responses,
                'updated_at': eval_form.updated_at if hasattr(eval_form, 'updated_at') else None,
                'question_nodes': question_nodes
            }
        return None

    def get_status(self, obj):
        """Obtener estado completo"""
        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            recommendation = obj.get_or_create_recommendation()
            
            status_color = self.get_recommendation_attribute(obj, 'status_color', 'gris')
            status_info = self.STATUS_COLORS.get(status_color, self.STATUS_COLORS['gris'])
            
            return {
                'color': status_info['color'],
                'text': status_info['text'],
                'is_completed': bool(evaluation_form.completed_date),
                'is_draft': self.get_recommendation_attribute(obj, 'is_draft', True),
                'last_updated': self.get_recommendation_attribute(obj, 'updated_at'),
                'professional_reviewed': (
                    bool(evaluation_form.professional_responses) 
                    if obj.template.evaluation_type == 'PROFESSIONAL' 
                    else None
                )
            }
        except Exception as e:
            print(f"Error getting status: {str(e)}")
            return self.get_default_status()

    def get_recommendations(self, obj):
        """Obtener recomendaciones"""
        if not obj.template:
            return None

        try:
            status = self.get_status(obj)
            recommendation = obj.get_or_create_recommendation()

            # Obtener información del profesional directamente del objeto
            professional_info = None
            professional_role = None
            
            if recommendation:
                if hasattr(recommendation, 'professional_name') and recommendation.professional_name:
                    professional_info = recommendation.professional_name
                elif hasattr(recommendation, 'updated_by') and recommendation.updated_by:
                    professional_info = recommendation.updated_by
                    
                if hasattr(recommendation, 'professional_role') and recommendation.professional_role:
                    professional_role = recommendation.professional_role
            
            base_recommendation = {
                'status': {
                    'color': status['color'],
                    'text': status['text']
                },
                'text': recommendation.text if recommendation else None,
                'updated_at': recommendation.updated_at if recommendation else None,
                'is_draft': recommendation.is_draft if recommendation else True,
                'professional': {
                    'name': professional_info,
                    'role': professional_role
                } if professional_info else None
            }

            return base_recommendation
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return None

    def get_training_form(self, obj):
        return self.get_template_attribute(obj, 'training_form')

    def get_default_status(self):
        """Helper para obtener estado por defecto"""
        return {
            'color': self.STATUS_COLORS['gris']['color'],
            'text': self.STATUS_COLORS['gris']['text'],
            'is_completed': False,
            'is_draft': True,
            'last_updated': None,
            'professional_reviewed': None
        }
