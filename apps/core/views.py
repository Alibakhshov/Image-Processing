import uuid
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

from .forms import ImageForm

from PIL import Image as PILImage, ImageOps
import numpy as np
from django.core.files.storage import default_storage
from django.conf import settings
import os
import cv2
import json



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

# def convert_to_negative_view(request, pk):
#     uploaded_image = Image.objects.get(pk=pk)
#     uploaded_image.resized_image = convert_to_negative(uploaded_image.original_image)
#     uploaded_image.save()
#     return redirect('ImageNegative')

# def convert_to_positive_view(request, pk):
#     uploaded_image = Image.objects.get(pk=pk)
#     uploaded_image.resized_image = convert_to_negative(uploaded_image.original_image)
#     uploaded_image.save()
#     return redirect('ImageNegative')

# Histogram Equalization
def histogram_equalization(img_path):
    # Open the image using PIL
    img = PILImage.open(img_path).convert('L')  # Convert to grayscale

    # Apply histogram equalization
    img_equalized = ImageOps.equalize(img)

    # Save the equalized image to a temporary file
    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_equalized_image.png')
    img_equalized.save(temp_path)

    return temp_path

def histEqual(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the original image
            instance = form.save()

            # Get the path of the uploaded image
            img_path = instance.original_image.path

            # Perform histogram equalization
            equalized_image_path = histogram_equalization(img_path)

            # Save the path of the equalized image in the model
            instance.resized_image.name = default_storage.save('resized_images/equalized_image.png', open(equalized_image_path, 'rb'))

            # Pass histogram data to the template
            original_histogram, equalized_histogram = calculate_histograms(img_path, equalized_image_path)

            return render(request, 'pages/ImageEnhancement/HistogramEqualization/HistogramEqualization.html', {
                'form': form,
                'uploaded_image': instance,
                'original_histogram': json.dumps(original_histogram),
                'equalized_histogram': json.dumps(equalized_histogram),
            })
    else:
        form = ImageForm()

    return render(request, 'pages/ImageEnhancement/HistogramEqualization/HistogramEqualization.html', {'form': form})

def calculate_histograms(original_image_path, equalized_image_path):
    # Calculate histograms for both original and equalized images
    original_histogram = get_histogram_data(original_image_path)
    equalized_histogram = get_histogram_data(equalized_image_path)

    return original_histogram, equalized_histogram

def get_histogram_data(image_path):
    # Calculate the histogram data from the image
    img = cv2.imread(image_path, 0)  # Read the image in grayscale
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    hist = hist.tolist()
    return hist

# Contrast Stretching
from django.shortcuts import render
from .forms import ImageForm
from django.core.files.storage import default_storage
from django.http import HttpResponse
import cv2
import numpy as np
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO


def contrastStretch(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the original image
            instance = form.save()

            # Get the path of the uploaded image
            img_path = instance.original_image.path

            # Perform contrast stretching
            stretched_image = contrast_stretching(img_path)

            # Assign the stretched image to the instance
            instance.resized_image.save(stretched_image.name, stretched_image)

            # Pass histogram data to the template
            original_histogram, stretched_histogram = calculate_histograms(img_path, instance.resized_image.path)

            return render(request, 'pages/ImageEnhancement/ContrastStretching/ContrastStretching.html', {
                'form': form,
                'uploaded_image': instance,
                'original_histogram': json.dumps(original_histogram),
                'stretched_histogram': json.dumps(stretched_histogram),
            })
    else:
        form = ImageForm()

    return render(request, 'pages/ImageEnhancement/ContrastStretching/ContrastStretching.html', {'form': form})

def calculate_histograms(original_image_path, stretched_image_path):
    # Calculate histograms for both original and stretched images
    original_histogram = get_histogram_data(original_image_path)
    stretched_histogram = get_histogram_data(stretched_image_path)

    return original_histogram, stretched_histogram

def get_histogram_data(image_path):
    # Calculate the histogram data from the image
    img = cv2.imread(image_path, 0)  # Read the image in grayscale
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    hist = hist.tolist()
    return hist

from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import base64


def contrast_stretching(image_path):
    img = cv2.imread(image_path, 0)  # Read the image in grayscale

    # Calculate min and max pixel values
    min_val = np.min(img)
    max_val = np.max(img)

    # Apply contrast stretching formula
    stretched_img = ((img - min_val) / (max_val - min_val)) * 255

    # Convert to uint8 (required for saving with OpenCV)
    stretched_img = np.uint8(stretched_img)

    # Save the stretched image
    _, img_encoded = cv2.imencode('.png', stretched_img)

    # Convert to SimpleUploadedFile
    img_file = SimpleUploadedFile("stretched_image.png", img_encoded.tobytes(), content_type="image/png")

    return img_file

# ##################################Image compression##########################################################################
# In your views.py
# In your views.py
from django.shortcuts import render
from .forms import ImageForm
from .huffman_utils import read_binary_file, huffman_encode, write_binary_file, calculate_binary_size

def huffmanEncoding(request):
    print("Form submitted")

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")

            # Save the original image
            instance = form.save()

            # Get the path of the uploaded image
            img_path = instance.original_image.path

            # Print some information for debugging
            print(f"Image path: {img_path}")
            print(f"File size: {os.path.getsize(img_path)} bytes")

            # Read the binary data from the image file
            original_data = read_binary_file(img_path)

            if not original_data:
                return render(request, 'pages/ImageCompression/HuffmanCoding/HuffmanEncoding.html', {
                    'form': form,
                    'error_message': 'The uploaded image file is empty.',
                })

            # Print some information for debugging
            print(f"Original data size: {len(original_data)} bits")

            # Perform Huffman encoding
            encoded_data, huffman_tree = huffman_encode(original_data)

            # Save the encoded data to a binary file
            encoded_file_path = 'resized_images/encoded_data.bin'
            write_binary_file(encoded_data, encoded_file_path)

            # Save the path of the encoded image in the model
            instance.resized_image.name = 'resized_images/encoded_data.bin'
            instance.save()  # Save the instance with the resized_image path

            # Print some information for debugging
            print(f"Encoded data size: {len(encoded_data)} bits")

            # Convert binary data to a string of '0's and '1's
            original_binary_str = ''.join(str(bit) for bit in original_data)
            encoded_binary_str = ''.join(str(bit) for bit in encoded_data)

            # Calculate the sizes before and after encoding
            original_size = calculate_binary_size(img_path)
            encoded_size = calculate_binary_size(encoded_file_path)

            # Render the template with the updated data
            return render(request, 'pages/ImageCompression/HuffmanCoding/HuffmanEncoding.html', {
                'form': form,
                'uploaded_image': instance,
                'original_size': original_size,
                'encoded_size': encoded_size,
                'original_binary': original_binary_str,
                'encoded_binary': encoded_binary_str,
            })
        else:
            print("Form has validation errors")
            print(form.errors)  # Print the form errors for debugging
    else:
        form = ImageForm()

    return render(request, 'pages/ImageCompression/HuffmanCoding/HuffmanEncoding.html', {'form': form})

# ##################################Image segmentation##########################################################################


from django.shortcuts import render
from .forms import ImageSegmentationForm
from .models import Image
from PIL import Image
import numpy as np
from io import BytesIO
import os

def image_segmentation(request):
    if request.method == 'POST':
        form = ImageSegmentationForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()

            # Get the path of the uploaded image
            img_path = instance.original_image.path

            # Perform image segmentation using thresholding
            threshold = form.cleaned_data['threshold']
            segmented_image_path = segment_image(img_path, threshold)

            # Save the path of the segmented image in the model
            instance.segmented_image.name = segmented_image_path
            instance.save()

            return render(request, 'pages/ImageSegmentation/Threshold/Threshold.html', {'form': form, 'uploaded_image': instance})
    else:
        form = ImageSegmentationForm()

    return render(request, 'pages/ImageSegmentation/Threshold/Threshold.html', {'form': form})

from django.core.files.storage import default_storage

def segment_image(img_path, threshold):
    img = Image.open(img_path).convert('L')  # Convert to grayscale
    img_array = np.array(img)
    segmented_array = np.where(img_array > threshold, 255, 0)  # Apply thresholding
    segmented_img = Image.fromarray(segmented_array.astype(np.uint8))

    # Save the segmented image to BytesIO
    buffered = BytesIO()
    segmented_img.save(buffered, format="PNG")
    
    # Create a unique file name for the segmented image
    segmented_image_name = f'segmented_image_{threshold}.png'

    # Save the segmented image to the media root using Django's storage system
    segmented_image_path = default_storage.save(os.path.join('segmented_images', segmented_image_name), ContentFile(buffered.getvalue()))

    return segmented_image_path

# image segmentation using region based segmentation
from django.conf import settings
from .segmentation_utils import watershed_segmentation

from django.conf import settings

def regionBasedSegmentation(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()

            # Perform region-based segmentation (Watershed algorithm)
            segmented_image_path = watershed_segmentation(instance.original_image.path)

            # Get the URL of the segmented image
            original_image_url = instance.original_image.url
            segmented_image_url = original_image_url.replace(
                'images', 'segmented_images'
            ).replace(
                os.path.basename(original_image_url),
                os.path.basename(segmented_image_path)
            )

            return render(request, 'pages/ImageSegmentation/RegionBased/RegionBased.html', {
                'form': form,
                'uploaded_image': instance,
                'segmented_image_url': segmented_image_url,
            })
    else:
        form = ImageForm()

    return render(request, 'pages/ImageSegmentation/RegionBased/RegionBased.html', {'form': form})
