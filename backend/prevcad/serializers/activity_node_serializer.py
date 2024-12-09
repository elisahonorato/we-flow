from rest_framework import serializers
from ..models import (
    ActivityNodeDescription,
    TextQuestion,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    ScaleQuestion,
    ImageQuestion,
)

# Serializador base para ActivityNode
class ActivityNodeSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # Determinar el tipo de nodo
        if isinstance(instance, ActivityNodeDescription):
            return ActivityNodeDescriptionSerializer(instance).data
        elif isinstance(instance, TextQuestion):
            return TextQuestionSerializer(instance).data
        elif isinstance(instance, SingleChoiceQuestion):
            return SingleChoiceQuestionSerializer(instance).data
        elif isinstance(instance, MultipleChoiceQuestion):
            return MultipleChoiceQuestionSerializer(instance).data
        elif isinstance(instance, ScaleQuestion):
            return ScaleQuestionSerializer(instance).data
        elif isinstance(instance, ImageQuestion):
            return ImageQuestionSerializer(instance).data
        return super().to_representation(instance)

# Serializadores específicos para cada tipo de nodo
class ActivityNodeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityNodeDescription
        fields = '__all__'

class TextQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = '__all__'

class SingleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleChoiceQuestion
        fields = '__all__'

class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuestion
        fields = '__all__'

class ScaleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScaleQuestion
        fields = '__all__'

class ImageQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageQuestion
        fields = '__all__'
