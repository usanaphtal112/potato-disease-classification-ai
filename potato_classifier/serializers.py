from rest_framework import serializers
from .models import ImageClassification


class ImageClassificationSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(read_only=True)
    confidence_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = ImageClassification
        fields = [
            "id",
            "image",
            "image_url",
            "predicted_class",
            "confidence",
            "confidence_percentage",
            "all_predictions",
            "recommendations",
            "is_preprocessed",
            "processing_time",
            "image_size",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "predicted_class",
            "confidence",
            "confidence_percentage",
            "all_predictions",
            "recommendations",
            "is_preprocessed",
            "processing_time",
            "image_size",
            "created_at",
            "image_url",
        ]


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(
        help_text="Upload a potato plant image for disease classification. Supported formats: JPEG, PNG, WebP. Max size: 10MB"
    )

    def validate_image(self, value):
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image file too large. Maximum size is 10MB."
            )

        # Validate file format
        allowed_formats = ["JPEG", "PNG", "WEBP", "JPG"]
        if hasattr(value, "image"):
            if value.image.format not in allowed_formats:
                raise serializers.ValidationError(
                    f"Unsupported image format. Allowed formats: {', '.join(allowed_formats)}"
                )

        return value


class ClassificationResultSerializer(serializers.Serializer):
    """Serializer for classification response"""

    id = serializers.UUIDField()
    predicted_class = serializers.CharField()
    confidence = serializers.FloatField()
    confidence_percentage = serializers.FloatField()
    all_predictions = serializers.DictField()
    recommendations = serializers.ListField(child=serializers.CharField())
    is_preprocessed = serializers.BooleanField()
    processing_time = serializers.FloatField()
    image_url = serializers.URLField()
    message = serializers.CharField()
