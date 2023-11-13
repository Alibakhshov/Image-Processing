import cv2
import numpy as np
import os
from PIL import Image
from io import BytesIO

def watershed_segmentation(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Applying thresholding or other preprocessing if needed
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Noise removal using morphological operations
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # Sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Marker labelling
    _, markers = cv2.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Mark the region of unknown with 0
    markers[unknown == 255] = 0

    markers = cv2.watershed(img, markers)
    img[markers == -1] = [0, 0, 255]  # Mark segmented regions in red

    # Save the segmented image to BytesIO
    buffered = BytesIO()
    segmented_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    segmented_img.save(buffered, format="PNG")
    
    # Create a unique file name for the segmented image
    segmented_image_name = f'segmented_image_{os.path.basename(img_path)}'
    segmented_image_path = os.path.join('media', 'segmented_images', segmented_image_name)

    # Save the segmented image to the media root
    os.makedirs(os.path.dirname(segmented_image_path), exist_ok=True)
    with open(segmented_image_path, 'wb') as f:
        f.write(buffered.getvalue())

    return segmented_image_path

    