from django.urls import path
from .views import (
    ListTaskView,
    TaskDetailView,
    TaskCreateView,
    StartTaskView,
    TaskProgressUpdateView,
    TaskMoveView,
)

urlpatterns = [
    path("", ListTaskView.as_view(), name="task-list"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("create/", TaskCreateView.as_view(), name="task-create"),
    path("<int:pk>/start/", StartTaskView.as_view(), name="task-start"),
    path(
        "<int:pk>/progress/",
        TaskProgressUpdateView.as_view(),
        name="task-progress-update",
    ),
    path("<int:pk>/move/", TaskMoveView.as_view(), name="task-move"),
]
