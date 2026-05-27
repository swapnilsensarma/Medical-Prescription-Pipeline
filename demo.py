import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt


def clean_prescription_image(image_path):
    # 1. Read the image from the file
    # (Make sure 'prescription.jpg' is in the same folder as this script)
    img = cv.imread(image_path)

    if img is None:
        print("Error: Could not find the image. Check the file name and path.")
        return

    # 2. Convert to Grayscale
    # Color distracts the OCR model, so we drop it to black and white
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # 3. Apply Gaussian Blur
    # This smooths out the image and removes tiny paper textures or noise
    blurred = cv.GaussianBlur(gray, (5, 5), 0)

    # 4. Adaptive Thresholding (The Magic Step)
    # This handles uneven lighting/shadows on the paper.
    # It calculates the threshold for small regions of the image separately.
    thresh = cv.adaptiveThreshold(
        blurred,
        255,  # Max pixel value (pure white)
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # Method for thresholding
        cv.THRESH_BINARY,  # Output black and white
        11,  # Block size (size of the local region)
        2   # Constant subtracted from the mean
    )

    # 5. Display the Before & After using Matplotlib
    # This is great for Spyder so you can see exactly what the code did
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    # OpenCV loads in BGR, Matplotlib uses RGB, so we convert for accurate display
    plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Cleaned for OCR")
    plt.imshow(thresh, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    return thresh


# --- Run the function ---
# Change 'prescription.jpg' to the actual name of your test image
cleaned_image = clean_prescription_image('prescription.jpg')
