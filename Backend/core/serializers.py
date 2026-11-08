"""Serializers for the marketplace taxonomy and attribute definitions."""

from rest_framework import serializers

from .models import AttributeDefinition, AttributeOption


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ["value", "label", "sort_order"]
        read_only_fields = fields


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    sub_category = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = AttributeDefinition
        fields = [
            "id",
            "category",
            "sub_category",
            "name",
            "slug",
            "label",
            "data_type",
            "required",
            "filterable",
            "sortable",
            "unit",
            "min_value",
            "max_value",
            "sort_order",
            "options",
        ]
        read_only_fields = fields
