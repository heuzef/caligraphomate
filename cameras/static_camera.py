#!/usr/bin/env python

"""StaticCamera: A fake camera that replays the same image at every frame."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from lerobot.cameras.camera import Camera
from lerobot.cameras.configs import CameraConfig, ColorMode


@dataclass(kw_only=True)
class StaticCameraConfig(CameraConfig):
    """Configuration for StaticCamera.

    Attributes:
        image_path: Path to the image file to replay (optional if image array is provided later).
        fps: Frames per second (default: 30).
        width: Image width in pixels (will be inferred from image if not provided).
        height: Image height in pixels (will be inferred from image if not provided).
    """
    image_path: str | None = None
    fps: int = 30
    width: int | None = None
    height: int | None = None


class StaticCamera(Camera):
    """A camera implementation that replays a static image.

    This class is useful for testing, debugging, or simulation purposes where you want
    to use a fixed image instead of a live camera feed. The same image is returned
    on every frame capture.

    Args:
        config: StaticCameraConfig with optional image_path and resolution settings.
        image: Optional numpy array containing the image. If provided, this takes
               precedence over config.image_path.

    Example:
        # From file path
        config = StaticCameraConfig(image_path="test_image.png", fps=30)
        camera = StaticCamera(config)
        camera.connect()
        frame = camera.read()

        # From numpy array
        config = StaticCameraConfig(fps=30)
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        camera = StaticCamera(config, image=image)
        camera.connect()
        frame = camera.read()
    """

    def __init__(self, config: StaticCameraConfig, image: np.ndarray | None = None):
        """Initialize the static camera.

        Args:
            config: Camera configuration.
            image: Optional image array. If not provided, will be loaded from config.image_path.
        """
        super().__init__(config)
        self.config = config
        self._image: np.ndarray | None = image
        self._connected = False
        self._original_color_mode = ColorMode.BGR  # OpenCV loads as BGR by default

        # If image is provided directly, update dimensions
        if self._image is not None:
            self._update_dimensions_from_image()

    def _update_dimensions_from_image(self) -> None:
        """Update width and height from the loaded image."""
        if self._image is not None:
            h, w = self._image.shape[:2]
            if self.height is None:
                self.height = h
            if self.width is None:
                self.width = w

    def _load_image(self) -> None:
        """Load the image from the configured path."""
        if self._image is not None:
            return  # Image already loaded

        if self.config.image_path is None:
            raise ValueError("No image provided. Set image_path in config or pass image to constructor.")

        image_path = Path(self.config.image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load image using OpenCV (loads as BGR by default)
        self._image = cv2.imread(str(image_path))
        if self._image is None:
            raise ValueError(f"Failed to load image from: {image_path}")

        self._original_color_mode = ColorMode.BGR
        self._update_dimensions_from_image()

    def _convert_color_mode(self, image: np.ndarray, target_mode: ColorMode) -> np.ndarray:
        """Convert image between RGB and BGR color modes.

        Args:
            image: Input image array.
            target_mode: Target color mode (RGB or BGR).

        Returns:
            Converted image array.
        """
        if target_mode == self._original_color_mode:
            return image

        # Convert between RGB and BGR
        if target_mode == ColorMode.RGB and self._original_color_mode == ColorMode.BGR:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif target_mode == ColorMode.BGR and self._original_color_mode == ColorMode.RGB:
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image

    @property
    def is_connected(self) -> bool:
        """Check if the camera is connected.

        Returns:
            True if connected and image is loaded, False otherwise.
        """
        return self._connected and self._image is not None

    @staticmethod
    def find_cameras() -> list[dict[str, Any]]:
        """Find available static cameras.

        Since static cameras are not physical devices, this returns an empty list.

        Returns:
            Empty list.
        """
        return []

    def connect(self, warmup: bool = True) -> None:
        """Connect to the camera (load the image).

        Args:
            warmup: Ignored for static camera (included for interface compatibility).
        """
        if not self._connected:
            self._load_image()
            self._connected = True

    def read(self, color_mode: ColorMode | None = None) -> np.ndarray:
        """Capture and return a frame (the static image).

        Args:
            color_mode: Desired color mode (RGB or BGR). If None, returns in original mode.

        Returns:
            The static image as a numpy array.

        Raises:
            RuntimeError: If camera is not connected.
        """
        if not self.is_connected:
            raise RuntimeError("Camera not connected. Call connect() first.")

        image = self._image.copy()

        if color_mode is not None:
            image = self._convert_color_mode(image, color_mode)

        return image

    def async_read(self, timeout_ms: float = 1000.0) -> np.ndarray:
        """Asynchronously capture and return a frame (the static image).

        For StaticCamera, this is identical to read() since no actual async operation is needed.

        Args:
            timeout_ms: Ignored for static camera (included for interface compatibility).

        Returns:
            The static image as a numpy array.
        """
        return self.read()

    def disconnect(self) -> None:
        """Disconnect from the camera.

        Releases the image and marks the camera as disconnected.
        """
        self._connected = False
        # Optionally clear the image to free memory
        # self._image = None
