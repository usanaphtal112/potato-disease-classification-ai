from django.db import models
from cloudinary.models import CloudinaryField
import uuid


class ImageClassification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = CloudinaryField("image", folder="potato_classifications/")
    predicted_class = models.CharField(max_length=50)
    confidence = models.FloatField()
    all_predictions = models.JSONField()
    recommendations = models.JSONField()
    is_preprocessed = models.BooleanField(default=False)
    processing_time = models.FloatField(
        null=True, blank=True, help_text="Processing time in seconds"
    )
    image_size = models.CharField(
        max_length=20, null=True, blank=True, help_text="Original image dimensions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Image Classification"
        verbose_name_plural = "Image Classifications"

    def __str__(self):
        return f"{self.predicted_class} - {self.confidence:.2%} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def image_url(self):
        """Get the Cloudinary URL for the image"""
        return self.image.url if self.image else None

    @property
    def confidence_percentage(self):
        """Get confidence as percentage"""
        return round(self.confidence * 100, 2)
