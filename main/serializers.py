from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    starred_by = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "name", "description", "thumbnail", "starred_by"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def get_starred_by(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())