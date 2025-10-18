import numpy as np
import cv2
from pathlib import Path
from typing import Any
from lerobot.cameras.camera import Camera
from lerobot.cameras.configs import ColorMode
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from static_image_camera_config import StaticImageCameraConfig


class StaticImageCamera(Camera):
    """Camera implementation that reads from a static image file.
    
    This class simulates a camera by repeatedly returning the same static image.
    Useful for testing or when using pre-captured images as camera input.
    """

    def __init__(self, config: StaticImageCameraConfig):
        """Initialize the static image camera.
        
        Args:
            config: Camera configuration. The 'index_or_path' should contain 
                   the path to the image file.
        """
        super().__init__(config)
        self._connected = False
        self._image = None
        
        # Load image immediately if path is provided
        if hasattr(config, 'index_or_path') and config.index_or_path:
            self._load_image(config.index_or_path)

    def _load_image(self, warmup: bool = True) -> None:
        """Load image from file and handle errors."""
        try:
            path = config.path
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            self._image = cv2.imread(str(path))
            if self._image is None:
                raise ValueError(f"Failed to load image: {image_path}")
                
            # Resize if dimensions are specified in config
            if self.width is not None and self.height is not None:
                self._image = cv2.resize(self._image, (self.width, self.height))
                
            print(f"Loaded static image: {image_path} (shape: {self._image.shape})")
            
        except Exception as e:
            print(f"Error loading static image: {e}")
            raise

    @property
    def is_connected(self) -> bool:
        """Check if the static image is loaded and ready."""
        return self._connected and self._image is not None

    @staticmethod
    def find_cameras() -> list[dict[str, Any]]:
        """Static images don't have detectable cameras.
        
        Returns:
            Empty list since static images are file-based, not discoverable cameras.
        """
        return []

    def connect(self, warmup: bool = True) -> None:
        """Establish connection to the static image.
        
        Args:
            warmup: For compatibility with interface, no warmup needed for static images.
        """
        if self._image is None and hasattr(self, '_image_path'):
            self._load_image(self._image_path)
        
        self._connected = True
        print("Static image camera connected")

    def read(self, color_mode: ColorMode | None = None) -> np.ndarray:
        """Return the static image as a frame.
        
        Args:
            color_mode: Desired color mode for the output frame.
            
        Returns:
            np.ndarray: The static image as a numpy array.
            
        Raises:
            RuntimeError: If camera is not connected or image not loaded.
        """
        if not self.is_connected or self._image is None:
            raise RuntimeError("Static image camera not connected or image not loaded")
        color_mode = self.color_mode if color_mode is None else color_mode
        
        frame = self._image.copy()
        
        # Handle color mode conversion if needed
        if color_mode == ColorMode.RGB:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif color_mode == ColorMode.GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Add other color mode conversions as needed
            
        return frame

    def async_read(self, timeout_ms: float = 1000.0) -> np.ndarray:
        """Asynchronously read the static image.
        
        For static images, this is the same as synchronous read since there's no
        actual camera hardware involved.
        
        Args:
            timeout_ms: Maximum time to wait (for interface compatibility).
            
        Returns:
            np.ndarray: The static image as a numpy array.
        """
        return self.read()

    def disconnect(self) -> None:
        """Disconnect from the static image and release resources."""
        self._connected = False
        self._image = None
        print("Static image camera disconnected")

    def __del__(self):
        """Ensure proper cleanup when object is destroyed."""
        self.disconnect()
