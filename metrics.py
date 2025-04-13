import numpy as np
from PIL import Image
from tkinter import filedialog

def calculate_mse(image1, image2):
    """
    Calculate Mean Squared Error (MSE) between two images.
    """
    arr1 = np.array(image1)
    arr2 = np.array(image2)
    mse = np.mean((arr1 - arr2) ** 2)
    return mse

def calculate_psnr(image1, image2):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two images.
    """
    mse = calculate_mse(image1, image2)
    if mse == 0:
        return float('inf')  # Identical images
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def calculate_accuracy(image1, image2):
    """
    Calculate accuracy (percentage of matching pixels) between two images.
    """
    arr1 = np.array(image1)
    arr2 = np.array(image2)
    total_pixels = arr1.size
    matching_pixels = np.sum(arr1 == arr2)
    accuracy = (matching_pixels / total_pixels) * 100
    return accuracy

# Example Usage
original_image = Image.open("images/4k.jpg").convert("L")  # Convert to grayscale
encoded_decoded_image = Image.open("dist/decoded_hidden_image_4.png").convert("L")    # Convert to grayscale

mse = calculate_mse(original_image, encoded_decoded_image)
psnr = calculate_psnr(original_image, encoded_decoded_image)
accuracy = calculate_accuracy(original_image, encoded_decoded_image)

print(f"MSE: {mse:.2f}")
print(f"PSNR: {psnr:.2f} dB")
print(f"Accuracy: {accuracy:.2f}%")
