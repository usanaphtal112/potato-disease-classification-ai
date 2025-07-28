import numpy as np
import onnxruntime as ort
from PIL import Image
import io
import os
import time
from django.conf import settings

CLASS_NAMES = [
    "Bacteria",
    "Fungi",
    "Nematode",
    "Pest",
    "Pythopthora",
    "Virus",
    "Healthy",
]

DISEASE_RECOMMENDATIONS = {
    "Bacteria": [
        "Apply copper-based bactericides as preventive measure",
        "Ensure proper field drainage to reduce moisture",
        "Rotate crops with non-host plants for 2-3 years",
        "Remove and destroy infected plant debris",
        "Use certified disease-free seed potatoes",
    ],
    "Fungi": [
        "Apply fungicide treatments during favorable weather conditions",
        "Improve air circulation around plants by proper spacing",
        "Avoid overhead irrigation to reduce leaf wetness",
        "Practice crop rotation with non-susceptible crops",
        "Remove infected plant material and dispose properly",
    ],
    "Nematode": [
        "Use nematode-resistant potato varieties when available",
        "Apply organic soil amendments like compost to improve soil health",
        "Practice long-term crop rotation with non-host crops",
        "Consider soil solarization in heavily infested areas",
        "Use beneficial nematodes as biological control agents",
    ],
    "Pest": [
        "Monitor fields regularly for early pest detection",
        "Use integrated pest management (IPM) strategies",
        "Apply targeted insecticides only when threshold levels are reached",
        "Encourage beneficial insects by maintaining habitat diversity",
        "Remove weeds that may harbor pest insects",
    ],
    "Pythopthora": [
        "Improve soil drainage and avoid waterlogged conditions",
        "Apply preventive fungicide treatments during wet periods",
        "Plant in raised beds to improve drainage",
        "Use resistant potato varieties when available",
        "Avoid working in fields when plants are wet",
    ],
    "Virus": [
        "Control aphid vectors through insecticide applications",
        "Use certified virus-free seed potatoes",
        "Remove infected plants immediately to prevent spread",
        "Control weeds that may serve as virus reservoirs",
        "Practice good field sanitation and equipment cleaning",
    ],
    "Healthy": [
        "Continue current management practices as they are effective",
        "Monitor plants regularly for any signs of disease or stress",
        "Maintain proper fertilization and irrigation schedules",
        "Keep fields clean of weeds and plant debris",
        "Rotate crops to prevent soil-borne disease buildup",
    ],
}


def check_if_preprocessed(image_file):
    """
    Check if image appears to be preprocessed
    This is a simple heuristic - you can make it more sophisticated
    """
    try:
        img = Image.open(image_file)
        # Reset file pointer
        image_file.seek(0)

        # Check if image is already the target size
        if img.size == settings.TARGET_IMAGE_SIZE:
            return True

        # Check if image appears to be normalized (values between 0-1)
        img_array = np.array(img)
        if img_array.max() <= 1.0 and img_array.min() >= 0.0:
            return True

        return False
    except Exception:
        return False


def preprocess_image(image_file, target_size=(224, 224)):
    """Load and preprocess image identical to training pipeline"""
    try:
        start_time = time.time()
        img = Image.open(image_file).convert("RGB")
        original_size = f"{img.size[0]}x{img.size[1]}"
        img = img.resize(target_size)
        img_array = np.array(img).astype(np.float32) / 255.0
        processing_time = time.time() - start_time
        return (
            np.expand_dims(img_array, axis=0),
            original_size,
            processing_time,
        )  # Add batch dimension
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")


def run_onnx_inference(image_array):
    """Run inference using ONNX Runtime"""
    try:
        # Create ONNX inference session
        session = ort.InferenceSession(
            settings.MODEL_PATH, providers=["CPUExecutionProvider"]
        )

        # Extract input details
        input_meta = session.get_inputs()[0]
        input_name = input_meta.name
        expected_shape = input_meta.shape
        print(f"🔍 Model Input Name: {input_name}")
        print(f"📐 Expected Shape: {expected_shape}")

        # Resolve symbolic dimensions to None
        resolved_shape = [
            None if isinstance(dim, str) else dim for dim in expected_shape
        ]

        # Validate shape: ensure dimensions match, except symbolic ones
        if len(image_array.shape) != len(resolved_shape):
            raise ValueError(
                f"Dimension mismatch. Expected {len(resolved_shape)}D, got {len(image_array.shape)}D"
            )

        for i, (actual_dim, expected_dim) in enumerate(
            zip(image_array.shape, resolved_shape)
        ):
            if expected_dim is not None and actual_dim != expected_dim:
                raise ValueError(
                    f"Shape mismatch at dimension {i}: expected {expected_dim}, got {actual_dim}"
                )

        # Run ONNX inference
        output = session.run(None, {input_name: image_array.astype(np.float32)})
        return np.squeeze(output[0])  # Remove batch dimension if needed

    except Exception as e:
        raise ValueError(f"❌ Error during ONNX inference: {str(e)}")


# Update the main inference function
def run_tflite_inference(image_array):
    """Run inference using ONNX Runtime (renamed for compatibility)"""
    return run_onnx_inference(image_array)


def get_classification_results(predictions):
    """Process predictions and return formatted results"""
    # Get the predicted class (highest probability)
    predicted_class_idx = np.argmax(predictions)
    predicted_class = CLASS_NAMES[predicted_class_idx]
    confidence = float(predictions[predicted_class_idx])

    # Format all predictions
    all_predictions = {}
    for i, class_name in enumerate(CLASS_NAMES):
        all_predictions[class_name] = float(predictions[i])

    # Get recommendations for the predicted class
    recommendations = DISEASE_RECOMMENDATIONS.get(
        predicted_class,
        [
            "Consult with a plant pathologist for specific treatment recommendations",
            "Monitor the affected area closely for changes",
            "Consider laboratory testing for accurate diagnosis",
            "Implement general good agricultural practices",
            "Keep detailed records of symptoms and treatments",
        ],
    )

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "all_predictions": all_predictions,
        "recommendations": recommendations,
    }
