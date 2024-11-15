from django.urls import path
from .views import OCRView

app_name = "cv_ocr_api"

urlpatterns = [
    path('ocr/id/extract', OCRView.as_view(), name='scan')
]