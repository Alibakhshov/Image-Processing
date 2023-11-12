from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cropping/", views.cropping, name="cropping"),
    path('NearestNeighborInterpolation/', views.upload_image, name='NearestNeighborInterpolation'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('delete/<int:pk>/', views.delete_image, name='delete_image'),
    path('save/<int:pk>/', views.save_image, name='save_image'),
    path('image/negative/', views.home, name='ImageNegative'),
    path('convert_to_negative/<int:pk>/', views.convert_to_negative_view, name='convert_to_negative'),
    path('convert_to_positive/<int:pk>/', views.convert_to_positive_view, name='convert_to_positive'),
]