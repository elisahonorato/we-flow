from rest_framework import serializers
from django.db import models
from ..models import (
    ActivityNodeDescription,
    TextQuestion,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    ScaleQuestion,
    ImageQuestion,
    ResultNode
)

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
        elif isinstance(instance, ResultNode):
            return ResultNodeSerializer(instance).data

        return super().to_representation(instance)

# Serializadores específicos para cada tipo de nodo
class ActivityNodeDescriptionSerializer(serializers.ModelSerializer):
    next_node_type = serializers.CharField(write_only=True, required=False, allow_null=True)
    next_node_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ActivityNodeDescription
        fields = '__all__'
        extra_fields = ['next_node_type', 'next_node_id']

    def create(self, validated_data):
        next_node_type = validated_data.pop('next_node_type', None)
        next_node_id = validated_data.pop('next_node_id', None)

        instance = super().create(validated_data)

        if next_node_type and next_node_id:
            content_type = ContentType.objects.get(model=next_node_type.lower())
            instance.content_type = content_type
            instance.object_id = next_node_id
            instance.save()

        return instance

    def update(self, instance, validated_data):
        next_node_type = validated_data.pop('next_node_type', None)
        next_node_id = validated_data.pop('next_node_id', None)

        instance = super().update(instance, validated_data)

        if next_node_type and next_node_id:
            content_type = ContentType.objects.get(model=next_node_type.lower())
            instance.content_type = content_type
            instance.object_id = next_node_id
            instance.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.next_node:
            data['next_node_type'] = instance.next_node._meta.model_name
            data['next_node_id'] = instance.next_node.id
        return data

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


class ResultNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultNode
        fields = '__all__'