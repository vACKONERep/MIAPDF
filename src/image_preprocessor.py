"""
Image Preprocessing Module

Handles image preprocessing to improve OCR accuracy.
Includes noise reduction, contrast enhancement, deskewing, and binarization.
"""

import logging
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
from typing import Union, Tuple, Optional
import math

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Advanced image preprocessing for better OCR results.
    
    Optimized for handwritten Spanish forms with various preprocessing techniques.
    """
    
    def __init__(self):
        """Initialize the image preprocessor."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def preprocess_image(self, image: Union[Image.Image, np.ndarray], 
                        enhance_contrast: bool = True,
                        denoise: bool = True,
                        binarize: bool = True,
                        deskew: bool = True) -> np.ndarray:
        """
        Complete image preprocessing pipeline.
        
        Args:
            image: Input image (PIL Image or numpy array)
            enhance_contrast: Apply contrast enhancement
            denoise: Apply noise reduction
            binarize: Convert to binary (black/white)
            deskew: Correct image rotation
            
        Returns:
            Preprocessed image as numpy array
        """
        self.logger.info("Starting image preprocessing pipeline")
        
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image.copy()
            
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
        original_shape = img_array.shape
        
        # Step 1: Enhance contrast
        if enhance_contrast:
            img_array = self.enhance_contrast(img_array)
            self.logger.debug("Applied contrast enhancement")
            
        # Step 2: Noise reduction
        if denoise:
            img_array = self.reduce_noise(img_array)
            self.logger.debug("Applied noise reduction")
            
        # Step 3: Deskew image
        if deskew:
            img_array = self.deskew_image(img_array)
            self.logger.debug("Applied deskewing")
            
        # Step 4: Binarization
        if binarize:
            img_array = self.binarize_image(img_array)
            self.logger.debug("Applied binarization")
            
        self.logger.info(f"Preprocessing complete. Shape: {original_shape} -> {img_array.shape}")
        return img_array
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using multiple techniques.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Contrast-enhanced image
        """
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Additional gamma correction for handwriting
        gamma = 1.2
        lookupTable = np.empty((1, 256), np.uint8)
        for i in range(256):
            lookupTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
        enhanced = cv2.LUT(enhanced, lookupTable)
        
        return enhanced
    
    def reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction techniques.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Denoised image
        """
        # Non-local means denoising - good for preserving edges
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        
        # Additional morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return denoised
    
    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct image skew/rotation.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Deskewed image
        """
        # Find all non-zero points (text pixels)
        coords = np.column_stack(np.where(image > 0))
        
        if len(coords) < 100:  # Not enough points for reliable deskewing
            return image
            
        # Find minimum area rectangle
        rect = cv2.minAreaRect(coords)
        angle = rect[2]
        
        # Determine the correct angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image
            
        # Rotate image
        center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(image, rot_matrix, image.shape[1::-1], 
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        self.logger.debug(f"Deskewed by {angle:.2f} degrees")
        return deskewed
    
    def binarize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Convert to binary image using adaptive thresholding.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Binary image
        """
        # Use Otsu's method combined with Gaussian blur
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Adaptive thresholding as fallback for varying lighting
        adaptive = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Combine both methods
        combined = cv2.bitwise_and(binary, adaptive)
        
        return combined
    
    def remove_lines(self, image: np.ndarray) -> np.ndarray:
        """
        Remove form lines while preserving handwritten text.
        
        Args:
            image: Binary input image
            
        Returns:
            Image with lines removed
        """
        # Create kernels for line detection
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Combine line masks
        lines_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # Remove lines from original image
        result = cv2.subtract(image, lines_mask)
        
        return result
    
    def enhance_handwriting(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance handwritten text specifically.
        
        Args:
            image: Binary input image
            
        Returns:
            Enhanced image with better handwriting visibility
        """
        # Morphological operations to enhance handwriting
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        
        # Close gaps in characters
        enhanced = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Dilate slightly to make thin strokes more visible
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        enhanced = cv2.dilate(enhanced, kernel_dilate, iterations=1)
        
        return enhanced
    
    def crop_to_content(self, image: np.ndarray, padding: int = 20) -> np.ndarray:
        """
        Crop image to content boundaries with optional padding.
        
        Args:
            image: Input image
            padding: Padding around content in pixels
            
        Returns:
            Cropped image
        """
        # Find all non-zero points
        coords = np.column_stack(np.where(image > 0))
        
        if len(coords) == 0:
            return image
            
        # Get bounding box
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        # Add padding
        h, w = image.shape
        y_min = max(0, y_min - padding)
        x_min = max(0, x_min - padding)
        y_max = min(h, y_max + padding)
        x_max = min(w, x_max + padding)
        
        return image[y_min:y_max, x_min:x_max]
    
    def resize_image(self, image: np.ndarray, target_height: int = 2000) -> np.ndarray:
        """
        Resize image maintaining aspect ratio.
        
        Args:
            image: Input image
            target_height: Target height in pixels
            
        Returns:
            Resized image
        """
        h, w = image.shape
        if h <= target_height:
            return image
            
        # Calculate new dimensions
        aspect_ratio = w / h
        new_height = target_height
        new_width = int(new_height * aspect_ratio)
        
        # Resize with good interpolation
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        self.logger.debug(f"Resized from {w}x{h} to {new_width}x{new_height}")
        return resized