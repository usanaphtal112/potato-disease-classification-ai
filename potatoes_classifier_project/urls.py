"""
URL configuration for potatoes_classifier_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Potato Disease Classification API",
        default_version="v1",
        description="""
        # Potato Disease Classification API
        
        A comprehensive REST API for classifying potato plant diseases using deep learning.
        
        ## Features
        - **Smart Image Processing**: Automatic preprocessing detection and handling
        - **AI-Powered Classification**: Identifies 7 different conditions (6 diseases + healthy)
        - **Expert Recommendations**: Provides 5 actionable treatment recommendations
        - **Lightweight**: Uses ONNX Runtime for efficient inference
        - **Production Ready**: Built with Django REST Framework
        
        ## Disease Classes
        1. **Bacteria** - Bacterial infections in potato plants
        2. **Fungi** - Fungal diseases affecting potatoes
        3. **Nematode** - Nematode infestations
        4. **Pest** - Various pest damage
        5. **Pythopthora** - Pythopthora blight
        6. **Virus** - Viral infections
        7. **Healthy** - Healthy potato plants
        
        ## Usage Flow
        1. Upload an image via `/api/classify/`
        2. API automatically checks if preprocessing is needed
        3. Image is processed through AI model
        4. Returns classification with confidence scores
        5. Provides 5 specific treatment recommendations
        
        ## Response Format
        All endpoints return JSON responses with consistent error handling.
        """,
        terms_of_service="https://www.potatodiseaseclassification.com/terms/",
        contact=openapi.Contact(email="developer@potatodiseaseclassification.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("potato_classifier.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    # Documentation URLs
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
