import cv2
import numpy as np
from PIL import Image
import hashlib
import tkinter as tk
from tkinter import filedialog

def get_file_path():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

def hash_image(image_path):
    with open(image_path, 'rb') as f:
        img_hash = hashlib.md5(f.read()).hexdigest()
    return img_hash

def get_white_area_mask(mask):
    # Convert mask to numpy array
    mask_array = np.array(mask)
    
    # Threshold to binary image (detecting white area)
    _, thresholded = cv2.threshold(mask_array, 200, 255, cv2.THRESH_BINARY)
    return thresholded

def overlay_image_on_card(poker_card_path, input_image_path):
    
    # Load the mask and input image
    mask_image = cv2.imread(poker_card_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel
    input_image = cv2.imread(input_image_path)  # Your image to overlay

    # Ensure mask has an alpha channel
    if mask_image.shape[2] == 3:  # If no alpha channel, add one
        mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2BGRA)

    # Extract the alpha channel from the mask
    alpha_mask = mask_image[:, :, 3]  # Extract alpha channel

    # Get the dimensions of the mask image
    mask_height, mask_width = mask_image.shape[:2]

    # Get the input image dimensions
    h, w = input_image.shape[:2]
    aspect_ratio = w / h  # Width-to-height ratio

    # Determine how to resize (cover the entire mask)
    if aspect_ratio > (mask_width / mask_height):  # Input is more horizontal
        # Fit height first, then crop width
        new_width = int(mask_height * aspect_ratio)
        new_height = mask_height
    else:  # Input is more vertical
        # Fit width first, then crop height
        new_width = mask_width
        new_height = int(new_width / aspect_ratio)


    # Resize input image to ensure it covers the mask area completely
    resized_input = cv2.resize(input_image, (new_width, new_height))

    # Center crop the resized image to exactly fit the mask dimensions
    x_start = (new_width - mask_width) // 2
    y_start = (new_height - mask_height) // 2
    cropped_input = resized_input[y_start:y_start + mask_height, x_start:x_start + mask_width]

    # Ensure cropped input has an alpha channel
    cropped_input = cv2.cvtColor(cropped_input, cv2.COLOR_BGR2BGRA)

    # Apply the alpha mask to the cropped input image
    cropped_input[:, :, 3] = alpha_mask  # Assign mask transparency to the final output

    # Generate hashed filename
    img_hash = hash_image(input_image_path)
    output_path = f"output_painted_card_{img_hash}.png"
    
    # Save the final image
    cv2.imwrite(f"{output_path}.png", cropped_input, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    print(f"Final image saved as: {output_path}")


# Example usage
poker_card_path = "empty.png"  # Your poker card with transparency
input_image_path = get_file_path()  # Open file picker for input image

overlay_image_on_card(poker_card_path, input_image_path)
