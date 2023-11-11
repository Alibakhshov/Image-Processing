from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cropping/", views.cropping, name="cropping"),
    path('upload/', views.upload_image, name='upload_image'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('delete/<int:pk>/', views.delete_image, name='delete_image'),
]