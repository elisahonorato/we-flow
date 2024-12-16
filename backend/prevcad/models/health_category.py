from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .activity_node import ActivityNode, ActivityNodeDescription, ResultNode
import json

# The admin creates this instance

class CategoryTemplate(models.Model):
    icon = models.ImageField(upload_to='health_categories_icons/')
    name = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    evaluation_form = models.JSONField(null=True, blank=True, default=dict)

    def add_activity_node(self, node_data):
        """
        Adds an activity node to the evaluation form
        """
        if self.evaluation_form is None:
            self.evaluation_form = {'nodes': [], 'next_node_id': 1}
        
        if 'nodes' not in self.evaluation_form:
            self.evaluation_form['nodes'] = []
            
        if 'next_node_id' not in self.evaluation_form:
            self.evaluation_form['next_node_id'] = 1

        # Asignar un ID único al nodo
        node_id = self.evaluation_form['next_node_id']
        node_data['id'] = node_id
        self.evaluation_form['next_node_id'] = node_id + 1

        # Si hay nodos previos, conectar con el último
        if self.evaluation_form['nodes']:
            last_node = self.evaluation_form['nodes'][-1]
            last_node['next_node_id'] = node_id

        # Agregar el nuevo nodo
        self.evaluation_form['nodes'].append(node_data)
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new instances
            super().save(*args, **kwargs)
            root_node = ActivityNodeDescription.objects.create(
                type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
                description=self.description
            )
            for user in User.objects.all():
                HealthCategory.objects.create(
                    user=user,
                    template=self,
                    root_node=root_node
                )
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.description}"


class HealthCategory(models.Model):
    template = models.ForeignKey(CategoryTemplate, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_categories')
    root_node = models.ForeignKey(ActivityNodeDescription, on_delete=models.SET_NULL, null=True, blank=True)
    evaluation_form = models.JSONField(null=True, blank=True)
    responses = models.JSONField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    recommendations = models.JSONField(null=True, blank=True)
    readonly_fields = ['evaluation_form']  # Hacer `evaluation_form` de solo lectura aquí


    def save(self, *args, **kwargs):
        # Bloquear cambios en `evaluation_form`
        if self.pk:  # Si la instancia ya existe
            original = HealthCategory.objects.get(pk=self.pk)
            if self.evaluation_form != original.evaluation_form:
                raise ValueError("The evaluation_form field cannot be edited directly.")
            super().save(*args, **kwargs)


    def update_evaluation(self, responses: dict):
        """
        Updates the evaluation field with the provided responses.

        Args:
            responses (dict): A dictionary mapping ActivityNode IDs to answers.
        """
        activity_nodes = self.template.get_activity_nodes()
        node_ids = {str(node.id) for node in activity_nodes}

        # Validar respuestas
        for node in activity_nodes:
            if node.type == ActivityNode.NodeType.QUESTION and str(node.id) not in responses:
                raise ValueError(f"Question '{node.description}' is required but not answered.")

        # Guardar las respuestas
        self.evaluation = {"responses": responses}
        self.save()

    def process_evaluation_test(self, evaluation_test: dict) -> dict:
        """
        Processes an evaluation test and generates an evaluation result.

        Args:
            evaluation_test (dict): A dictionary containing test data for evaluation.

        Returns:
            dict: The evaluation result based on the test data.
        """
        activity_nodes = self.template.get_activity_nodes()
        result = {"evaluation_result": {}}

        for node in activity_nodes:
            node_id = str(node.id)
            if node.type == ActivityNode.NodeType.QUESTION and node_id in evaluation_test:
                answer = evaluation_test[node_id]
                # Example processing: Validate or compute result based on the answer
                result["evaluation_result"][node_id] = {
                    "question": node.description,
                    "answer": answer,
                    "is_correct": self.validate_answer(node, answer)  # Example validation method
                }

        return result

    def validate_answer(self, node: ActivityNode, answer: Any) -> bool:
        """
        Validates an answer for a specific node.

        Args:
            node (ActivityNode): The activity node to validate.
            answer (Any): The answer provided.

        Returns:
            bool: True if the answer is valid, False otherwise.
        """
        # Example validation logic; customize as needed
        if node.type == ActivityNode.NodeType.SINGLE_CHOICE:
            return answer in node.options
        return True

    @classmethod
    def create_categories_for_user(cls, user):
        templates = CategoryTemplate.objects.filter(is_active=True)
        for template in templates:
            root_node = ActivityNodeDescription.objects.create(
                type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
                description=template.description
            )

            cls.objects.create(
                user=user,
                template=template,
                root_node=root_node,

            )

@receiver(post_save, sender=User)
def create_user_health_categories(sender, instance, created, **kwargs):
    if created:
        HealthCategory.create_categories_for_user(instance)
