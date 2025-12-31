from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User


class TaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source="creator.username")
    assignee_name = serializers.ReadOnlyField(source="assignee.username")

    class Meta:
        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description"]

    def create(self, validated_data):
        # automatically set creator and leave assignee as None
        validated_data["creator"] = self.context["request"].user
        validated_data["assignee"] = None
        validated_data["progress"] = 0
        validated_data["column"] = "To Do"
        return super().create(validated_data)


class TaskProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["progress"]

    def validate_progress(self, value):
        if not 1 <= value <= 100:
            raise serializers.ValidationError("Progress must be between 1 and 100.")
        return value


class TaskMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["column"]

    def validate_column(self, value):
        allowed = ["To Do", "In Progress", "Completed"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid column.")
        return value
