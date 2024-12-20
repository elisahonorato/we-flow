from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response

from prevcad.models import (
  PhysicalActivity,
  Form,
  FormResponse,
  FormQuestion,
  QuestionResponse,
  HealthCategory,
  RootNode,
  EvaluationForm
)
from prevcad.serializers.form_serializer import (
  FormSerializer
)
from prevcad.serializers.health_category_serializer import (
  HealthCategorySerializer
)



class FormView(viewsets.ModelViewSet):
  queryset = Form.objects.all()
  serializer_class = FormSerializer

  def list(self, request: Request) -> Response:
    category_id = request.query_params.get('category_id')
    form_id = request.query_params.get('form_id')

    queryset = self.queryset
    if category_id:
      queryset = queryset.filter(category_id=category_id)
    if form_id:
      queryset = queryset.filter(id=form_id)

    serializer = self.serializer_class(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class FormByCategoryTestView(APIView):
  def get(self, request, category_id, *args, **kwargs):
    try:
      category = PhysicalActivity.objects.get(id=category_id)
      form = category.forms.filter(type=Form.TYPE_CHOICES.TEST).first()

      if not form:
        return Response({'error': 'No se encontró un formulario de test para esta categoría'}, status=status.HTTP_404_NOT_FOUND)

      serializer = FormSerializer(form)
      return Response(serializer.data, status=status.HTTP_200_OK)

    except PhysicalActivity.DoesNotExist:
      return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)

  def post(self, request, category_id, *args, **kwargs):
    try:
      # Obtener el formulario de tipo "TEST"
      category = PhysicalActivity.objects.get(id=category_id)
      form = category.forms.filter(type=Form.TYPE_CHOICES.TEST).first()
      if not form:
        return Response({'error': 'No se encontró un formulario de test para esta categoría'}, status=status.HTTP_404_NOT_FOUND)

      # Obtener el usuario y los datos de respuesta
      user = request.user  # Asume que el usuario está autenticado
      responses_data = request.data.get('responses', [])

      # Verificar si ya existe una respuesta previa para este formulario y usuario
      form_response, created = FormResponse.objects.get_or_create(form=form, user=user)

      # Actualizar o crear respuestas para cada pregunta
      for response in responses_data:
        question_id = response.get('question_id')
        answer = response.get('answer')
        try:
          question = form.questions.get(id=question_id)
          # Actualizar o crear una nueva respuesta para la pregunta
          question_response, _ = QuestionResponse.objects.update_or_create(
            form_response=form_response,
            question=question,
            defaults={
              'answer_text': answer if question.question_type == 'text' else None,
              'selected_option': answer if question.question_type == 'multiple_choice' else None
            }
          )
        except FormQuestion.DoesNotExist:
          return Response({'error': f'Pregunta con ID {question_id} no encontrada en este formulario'}, status=status.HTTP_400_BAD_REQUEST)

      return Response({'message': 'Respuestas actualizadas con éxito' if not created else 'Respuestas guardadas con éxito'}, status=status.HTTP_200_OK)

    except PhysicalActivity.DoesNotExist:
      return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)


class LastTestResultsView(APIView):
  def get(self, request, category_id, *args, **kwargs):
    try:
      category = PhysicalActivity.objects.get(id=category_id)
      form = category.forms.filter(type=Form.TYPE_CHOICES.TEST).first()
      if not form:
        return Response({'error': 'No se encontró un formulario de test para esta categoría'}, status=status.HTTP_404_NOT_FOUND)

      form_response = FormResponse.objects.filter(form=form, user=request.user).order_by('-id').first()
      if not form_response:
        return Response({'error': 'No se encontró ningún resultado previo para este test'}, status=status.HTTP_404_NOT_FOUND)

      response_data = {
        'form': FormSerializer(form).data,
        'responses': [
          {
            'question': question_response.question.question_text,
            'answer': question_response.answer_text or question_response.selected_option
          }
          for question_response in form_response.question_responses.all()
        ]
      }

      return Response(response_data, status=status.HTTP_200_OK)

    except PhysicalActivity.DoesNotExist:
      return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)


class HealthCategoryViewSet(viewsets.ModelViewSet):
    queryset = HealthCategory.objects.all()
    serializer_class = HealthCategorySerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        
        # Crear la categoría con root node automático
        category = HealthCategory.objects.create(
            name=data['name'],
            description=data['description'],
            icon=data.get('icon', 'default-icon')
        )

        # Crear y vincular root node automáticamente
        root_node = RootNode.objects.create(
            type="ROOT_NODE",
            description=data['description'],
            first_button_text="Comenzar evaluación",
        )

        # Crear y vincular form
        evaluation_form = EvaluationForm.objects.create()

        category.root_node = root_node
        category.evaluation_form = evaluation_form
        category.save()

        serializer = self.get_serializer(category)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
