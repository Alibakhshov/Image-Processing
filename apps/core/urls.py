from django.urls import path
from .views import dashboard, cropping

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("cropping/", cropping, name="cropping"),
]