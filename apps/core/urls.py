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
    path('histogram/equalization/', views.histEqual, name='HistogramEqualization'),
    path('contrast/stretching/', views.contrastStretch, name='ContrastStretching'),
    path('huffman/encoding/', views.huffmanEncoding, name='HuffmanEncoding'),
    path('thresholding/', views.image_segmentation, name='Thresholding'),
    path('regionBasedSegmentation/', views.regionBasedSegmentation, name='RegionBasedSegmentation'),
]