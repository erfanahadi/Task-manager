from rest_framework.views import APIView
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskProgressSerializer,
    TaskMoveSerializer,
)
from .models import Task
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsTaskOwner
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse


class ListTaskView(APIView):
    """
    List all tasks gropued by column
    """

    serializer_class = TaskSerializer

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Tasks grouped by column",
                response=TaskSerializer(many=True),
            )
        }
    )
    def get(self, request):
        tasks = Task.objects.all()
        columns = ["To Do", "In Progress", "Completed"]
        grouped_tasks = {}
        for column in columns:
            tasks_by_column = tasks.filter(column=column)
            serializer = TaskSerializer(tasks_by_column, many=True)
            grouped_tasks[column] = serializer.data

        return Response(grouped_tasks, status=status.HTTP_200_OK)


class TaskDetailView(APIView):
    """
    Retrieve, update or delete a task instance.
    """

    permission_classes = [IsAuthenticated, IsTaskOwner]
    serializer_class = TaskSerializer

    def get_object(self, pk):
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(self.request, task)
        return task

    @extend_schema(responses=TaskSerializer)
    def get(self, request, pk):
        task = self.get_object(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=TaskSerializer,
        responses=TaskSerializer,
    )
    def patch(self, request, pk):
        task = self.get_object(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Task deleted"),
            403: OpenApiResponse(description="Not allowed"),
        }
    )
    def delete(self, request, pk):
        task = self.get_object(pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCreateView(CreateAPIView):
    """
    Create a new task.
    """

    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    @extend_schema(
        request=TaskCreateSerializer,
        responses={201: TaskSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class StartTaskView(APIView):
    """
    Send id of the task to start a task. This user is assigned to the task. the task is moved to "In Progress"
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    @extend_schema(
        request=None,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Invalid task state"),
        },
    )
    @transaction.atomic
    def post(self, request, pk):
        task = Task.objects.select_for_update().get(pk=pk)

        if task.column != "To Do":
            return Response(
                {"detail": "Task cannot be started from its current state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if task.assignee is not None:
            return Response(
                {"detail": "Task is already assigned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.assignee = request.user
        task.column = "In Progress"
        task.progress = 1
        task.save(update_fields=["assignee", "column", "progress"])

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskProgressUpdateView(APIView):
    """
    Update the progress of a task from 1 to 100. This endpoint is only accessible to the assignee.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskProgressSerializer

    @extend_schema(
        request=TaskProgressSerializer,
        responses={
            200: TaskProgressSerializer,
            400: OpenApiResponse(description="Invalid progress value"),
            403: OpenApiResponse(description="Only assignee allowed"),
        },
    )
    @transaction.atomic
    def patch(self, request, pk):
        task = get_object_or_404(Task.objects.select_for_update(), pk=pk)

        # Permission check
        if task.assignee != request.user:
            return Response(
                {"detail": "Only the assignee can update progress."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskProgressSerializer(task, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        progress = serializer.validated_data["progress"]

        task.progress = progress

        if progress == 100:
            task.column = "Completed"
        if 1 <= progress < 100:
            task.column = "In Progress"
        if progress == 0:
            task.column = "To Do"
            task.assignee = None
        task.save()

        return Response(
            {
                "id": task.id,
                "progress": task.progress,
                "column": task.column,
            },
            status=status.HTTP_200_OK,
        )


class TaskMoveView(APIView):
    """
    Move a task from in progress to completed. This endpoint is only accessible to the creator or assignee
    If the task is moved to completed, the progress is set to 100.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskMoveSerializer

    @extend_schema(
        request=TaskMoveSerializer,
        responses={
            200: TaskMoveSerializer,
            403: OpenApiResponse(description="Not allowed to move task"),
        },
    )
    @transaction.atomic
    def patch(self, request, pk):
        task = get_object_or_404(Task.objects.select_for_update(), pk=pk)

        # Only creator or assignee can move tasks
        if request.user not in [task.creator, task.assignee]:
            return Response(
                {"detail": "You cannot move this task."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskMoveSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_column = serializer.validated_data["column"]

        task.column = new_column

        # Reverse invariant
        if new_column == "Completed":
            task.progress = 100

        if new_column == "In Progress":
            task.progress = 1

        if new_column == "To Do":
            task.progress = 0
            task.assignee = None

        task.save()

        return Response(
            {
                "id": task.id,
                "column": task.column,
                "progress": task.progress,
            },
            status=status.HTTP_200_OK,
        )
