from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html")

def cropping(request):
    return render(request, "pages/ImageResizing/cropper.html")

from django.shortcuts import render, redirect
from .models import Image
from .forms import ImageForm
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.contrib import messages


def resize_image(image_path, width, height):
    image = PILImage.open(image_path)
    resized_image = image.resize((width, height), PILImage.NEAREST)

    output_io = BytesIO()
    resized_image.save(output_io, format='JPEG')
    output_io.seek(0)

    image_name = image_path.name.split(".")[0]
    content_file = ContentFile(output_io.read())
    return InMemoryUploadedFile(content_file, 'ImageField', f'{image_name}_resized.jpg', 'image/jpeg', content_file.size, None)

def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)

            # Resize the image using Nearest-Neighbor Interpolation
            if image.width and image.height:
                image.resized_image = resize_image(image.original_image, image.width, image.height)
            image.save()
            return redirect('image_detail', pk=image.pk)
    else:
        form = ImageForm()
    return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/upload_image.html', {'form': form})

def image_detail(request, pk):
    try:
        image = Image.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/image_not_found.html')

    return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/image_detail.html', {'image': image})

def delete_image(request, pk):
    try:
        image = Image.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/image_not_found.html')

    if request.method == 'POST':
        # Check if the user has confirmed the deletion
        if request.POST.get('confirm_delete') == 'yes':
            # Delete files from media folder
            if image.original_image:
                path = os.path.join(settings.MEDIA_ROOT, str(image.original_image))
                os.remove(path)
            
            if image.resized_image:
                path = os.path.join(settings.MEDIA_ROOT, str(image.resized_image))
                os.remove(path)

            # Delete the database entry
            image.delete()
            return redirect('upload_image')
    
    return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/delete_image.html', {'image': image})

def save_image(request, pk):
    try:
        image = Image.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/image_not_found.html')

    if request.method == 'POST':
        # Check if the user has confirmed the save
        if request.POST.get('confirm_save') == 'yes':
            # Save the resized image
            image.original_image = image.resized_image
            image.resized_image = None
            image.save()
            messages.success(request, 'Image saved successfully')
            return redirect('image_detail', pk=image.pk)
    
    return render(request, 'pages/ImageResizing/Nearest-Neighbor-Interpolation/save_image.html', {'image': image})