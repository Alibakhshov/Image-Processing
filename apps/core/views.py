from django.shortcuts import render
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

def dashboard(request):
    return render(request, "dashboard.html")

def cropping(request):
    return render(request, "pages/ImageResizing/cropper.html")

# ##################################Image resizing##########################################################################

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
            return redirect('NearestNeighborInterpolation')
    
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

# ##################################Image enhancement##########################################################################

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Image
from PIL import Image as PilImage
import numpy as np
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def convert_to_negative(image):
    img = PilImage.open(image)
    img_array = np.array(img)
    negative_array = 255 - img_array
    negative_img = PilImage.fromarray(negative_array.astype('uint8'))
    buffer = BytesIO()
    negative_img.save(buffer, format='JPEG')
    return InMemoryUploadedFile(buffer, None, f'negative_{image.name}', 'image/jpeg', buffer.tell(), None)

def home(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            uploaded_image.resized_image = convert_to_negative(uploaded_image.original_image)
            uploaded_image.save()
            return render(request, 'pages/ImageEnhancement/ImageNegative/ImageNegative.html', {'form': form, 'uploaded_image': uploaded_image})
    else:
        form = ImageForm()
    return render(request, 'pages/ImageEnhancement/ImageNegative/ImageNegative.html', {'form': form})

def convert_to_negative_view(request, pk):
    uploaded_image = Image.objects.get(pk=pk)
    uploaded_image.resized_image = convert_to_negative(uploaded_image.original_image)
    uploaded_image.save()
    return redirect('ImageNegative')

def convert_to_positive_view(request, pk):
    uploaded_image = Image.objects.get(pk=pk)
    uploaded_image.resized_image = convert_to_negative(uploaded_image.original_image)
    uploaded_image.save()
    return redirect('ImageNegative')