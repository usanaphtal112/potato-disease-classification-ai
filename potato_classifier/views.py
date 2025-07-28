from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
import time

from .models import ImageClassification
from .serializers import (
    ImageClassificationSerializer,
    ImageUploadSerializer,
    ClassificationResultSerializer,
)
from .utils import (
    check_if_preprocessed,
    preprocess_image,
    run_onnx_inference,
    get_classification_results,
)


class ClassifyImageView(APIView):
    """
    Classify potato disease from uploaded image

    Upload an image of a potato plant to get disease classification results
    with confidence scores and specific treatment recommendations.
    """

    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Classify Potato Disease",
        operation_description="""
        Upload a potato plant image for disease classification.
        
        **Process:**
        1. Image preprocessing check and optimization
        2. ML model inference using ONNX Runtime
        3. Disease classification with confidence scores
        4. Generate 5 specific treatment recommendations
        5. Store results with Cloudinary image hosting
        
        **Supported Disease Classes:**
        - Bacteria
        - Fungi
        - Nematode
        - Pest
        - Pythopthora
        - Virus
        - Healthy
        
        **Image Requirements:**
        - Format: JPEG, PNG, WebP
        - Max size: 10MB
        - Recommended: Clear, well-lit potato plant images
        """,
        request_body=ImageUploadSerializer,
        responses={
            200: openapi.Response(
                description="Classification successful",
                schema=ClassificationResultSerializer,
                examples={
                    "application/json": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "predicted_class": "Fungi",
                        "confidence": 0.92,
                        "confidence_percentage": 92.0,
                        "all_predictions": {
                            "Bacteria": 0.05,
                            "Fungi": 0.92,
                            "Nematode": 0.01,
                            "Pest": 0.01,
                            "Pythopthora": 0.01,
                            "Virus": 0.00,
                            "Healthy": 0.00,
                        },
                        "recommendations": [
                            "Apply fungicide treatments during favorable weather conditions",
                            "Improve air circulation around plants by proper spacing",
                            "Avoid overhead irrigation to reduce leaf wetness",
                            "Practice crop rotation with non-susceptible crops",
                            "Remove infected plant material and dispose properly",
                        ],
                        "is_preprocessed": False,
                        "processing_time": 1.23,
                        "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/potato_classifications/sample.jpg",
                        "message": "Image classified successfully",
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request - Invalid image or preprocessing error",
                examples={
                    "application/json": {
                        "error": "Image file too large. Maximum size is 10MB."
                    }
                },
            ),
            500: openapi.Response(
                description="Server error - Model not found or inference error",
                examples={
                    "application/json": {
                        "error": "Model file not found. Please ensure the ONNX model is in the correct location."
                    }
                },
            ),
        },
        tags=["Classification"],
    )
    def post(self, request, *args, **kwargs):
        """
        Classify potato disease from uploaded image
        """
        serializer = ImageUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_time = time.time()
            image_file = serializer.validated_data["image"]

            # Check if model file exists
            if not os.path.exists(settings.MODEL_PATH):
                return Response(
                    {
                        "error": "Model file not found. Please ensure the ONNX model is in the correct location."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Step 1: Check if image is preprocessed
            is_preprocessed = check_if_preprocessed(image_file)

            # Step 2: Preprocess if needed
            preprocessed_image, original_size, preprocess_time = preprocess_image(
                image_file, settings.TARGET_IMAGE_SIZE
            )

            # Step 3: Run inference
            predictions = run_onnx_inference(preprocessed_image)

            # Step 4: Get classification results and recommendations
            results = get_classification_results(predictions)

            # Calculate total processing time
            total_processing_time = time.time() - start_time

            # Step 5: Save to database with Cloudinary storage
            classification = ImageClassification.objects.create(
                image=image_file,
                predicted_class=results["predicted_class"],
                confidence=results["confidence"],
                all_predictions=results["all_predictions"],
                recommendations=results["recommendations"],
                is_preprocessed=is_preprocessed,
                processing_time=total_processing_time,
                image_size=original_size,
            )

            # Step 6: Return response
            response_data = {
                "id": classification.id,
                "predicted_class": results["predicted_class"],
                "confidence": results["confidence"],
                "confidence_percentage": classification.confidence_percentage,
                "all_predictions": results["all_predictions"],
                "recommendations": results["recommendations"],
                "is_preprocessed": is_preprocessed,
                "processing_time": round(total_processing_time, 2),
                "image_url": classification.image_url,
                "message": "Image classified successfully",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClassificationHistoryView(APIView):
    """
    Get classification history

    Retrieve a list of recent image classifications with pagination support.
    """

    @swagger_auto_schema(
        operation_summary="Get Classification History",
        operation_description="""
        Retrieve the latest 50 image classifications from the database.
        
        **Response includes:**
        - Classification ID and timestamp
        - Predicted disease class and confidence score
        - Cloudinary image URLs
        - Treatment recommendations
        - Processing metadata
        
        Results are ordered by creation date (newest first).
        """,
        responses={
            200: openapi.Response(
                description="Classification history retrieved successfully",
                schema=ImageClassificationSerializer(many=True),
            )
        },
        tags=["History"],
    )
    def get(self, request):
        classifications = ImageClassification.objects.all()[:50]  # Latest 50
        serializer = ImageClassificationSerializer(classifications, many=True)
        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK,
        )


class ClassificationDetailView(APIView):
    """
    Get specific classification details

    Retrieve detailed information about a specific classification by ID.
    """

    @swagger_auto_schema(
        operation_summary="Get Classification Details",
        operation_description="""
        Retrieve detailed information about a specific classification using its UUID.
        
        **Includes:**
        - Complete classification results
        - All prediction confidence scores
        - Treatment recommendations
        - Processing metadata
        - Cloudinary image URL
        """,
        responses={
            200: openapi.Response(
                description="Classification details retrieved successfully",
                schema=ImageClassificationSerializer,
            ),
            404: openapi.Response(
                description="Classification not found",
                examples={"application/json": {"error": "Classification not found"}},
            ),
        },
        tags=["History"],
    )
    def get(self, request, classification_id):
        try:
            classification = ImageClassification.objects.get(id=classification_id)
            serializer = ImageClassificationSerializer(classification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ImageClassification.DoesNotExist:
            return Response(
                {"error": "Classification not found"}, status=status.HTTP_404_NOT_FOUND
            )


class HealthCheckView(APIView):
    """
    API health check endpoint

    Check the status of the API and its dependencies.
    """

    @swagger_auto_schema(
        operation_summary="API Health Check",
        operation_description="""
        Check the health status of the API and its dependencies.
        
        **Checks:**
        - API server status
        - ONNX model availability
        - Database connectivity
        - Cloudinary configuration
        """,
        responses={
            200: openapi.Response(
                description="API is healthy",
                examples={
                    "application/json": {
                        "status": "healthy",
                        "model_loaded": True,
                        "model_path": "/path/to/model.onnx",
                        "cloudinary_configured": True,
                        "database_connected": True,
                        "timestamp": "2024-01-15T10:30:00Z",
                    }
                },
            )
        },
        tags=["System"],
    )
    def get(self, request):
        from django.db import connection
        from django.utils import timezone
        import cloudinary.api

        # Check model availability
        model_exists = os.path.exists(settings.MODEL_PATH)

        # Check database connectivity
        try:
            connection.ensure_connection()
            db_connected = True
        except Exception:
            db_connected = False

        # Check Cloudinary configuration
        try:
            cloudinary_configured = bool(
                settings.CLOUDINARY_STORAGE.get("CLOUD_NAME")
                and settings.CLOUDINARY_STORAGE.get("API_KEY")
                and settings.CLOUDINARY_STORAGE.get("API_SECRET")
            )
        except Exception:
            cloudinary_configured = False

        return Response(
            {
                "status": "healthy",
                "model_loaded": model_exists,
                "model_path": settings.MODEL_PATH,
                "cloudinary_configured": cloudinary_configured,
                "database_connected": db_connected,
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK,
        )
