from django.urls import path
from .views import (
    ClassifyImageView,
    ClassificationHistoryView,
    ClassificationDetailView,
    HealthCheckView,
)

urlpatterns = [
    path("classify/", ClassifyImageView.as_view(), name="classify-image"),
    path(
        "history/", ClassificationHistoryView.as_view(), name="classification-history"
    ),
    path(
        "classification/<uuid:classification_id>/",
        ClassificationDetailView.as_view(),
        name="classification-detail",
    ),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
