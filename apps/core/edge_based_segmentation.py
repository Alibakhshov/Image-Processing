import cv2
import os
import numpy as np
from PIL import Image
from io import BytesIO

def canny_edge_segmentation(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # Applying Gaussian blur to the image to reduce noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # Applying the Canny edge detector
    edges = cv2.Canny(blurred, 50, 150)

    # Save the segmented image to BytesIO
    buffered = BytesIO()
    Image.fromarray(edges).save(buffered, format="PNG")

    # Create a unique file name for the segmented image
    segmented_image_name = f'edge_segmented_image_{os.path.basename(img_path)}'
    segmented_image_path = os.path.join('media', 'segmented_images', segmented_image_name)

    # Save the segmented image to the media root
    os.makedirs(os.path.dirname(segmented_image_path), exist_ok=True)
    with open(segmented_image_path, 'wb') as f:
        f.write(buffered.getvalue())

    return segmented_image_path
