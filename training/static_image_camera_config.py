from pathlib import Path
from lerobot.cameras.configs import CameraConfig, ColorMode
from dataclasses import dataclass


@CameraConfig.register_subclass("static_image")
@dataclass
class StaticImageCameraConfig(CameraConfig):

    path: Path
    color_mode: ColorMode = ColorMode.RGB

    def __post_init__(self):
        if self.color_mode not in (ColorMode.RGB, ColorMode.BGR):
            raise ValueError(
                f"`color_mode` is expected to be {ColorMode.RGB.value} or {ColorMode.BGR.value}, but {self.color_mode} is provided."
            )
