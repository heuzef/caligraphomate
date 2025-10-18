#!/usr/bin/env python3
import os
import cv2
from pathlib import Path

# === CONFIGURATION ===
PNG_ROOT = "png"
OUTPUT_ROOT = "videos"
WIDTH = 640
HEIGHT = 480
FPS = 30
DURATION_S = 5  # durée de chaque vidéo en secondes

def create_static_video(png_path: str, output_path: str, width: int, height: int, fps: int, duration_s: int):
    """Crée une vidéo MP4 à partir d'une image PNG statique."""
    img = cv2.imread(png_path)
    if img is None:
        print(f"❌ Impossible de lire {png_path}")
        return
    
    # Redimensionne si nécessaire
    img = cv2.resize(img, (width, height))

    # Définition du codec et création du VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = int(fps * duration_s)
    for _ in range(frame_count):
        out.write(img)

    out.release()
    print(f"✅ Vidéo créée : {output_path}")

def main():
    for shape_dir in os.listdir(PNG_ROOT):
        shape_path = os.path.join(PNG_ROOT, shape_dir)
        if not os.path.isdir(shape_path):
            continue

        output_shape_dir = os.path.join(OUTPUT_ROOT, shape_dir)
        os.makedirs(output_shape_dir, exist_ok=True)

        for png_file in os.listdir(shape_path):
            if not png_file.lower().endswith(".png"):
                continue

            png_path = os.path.join(shape_path, png_file)
            mp4_file = os.path.splitext(png_file)[0] + ".mp4"
            output_path = os.path.join(output_shape_dir, mp4_file)

            create_static_video(png_path, output_path, WIDTH, HEIGHT, FPS, DURATION_S)

if __name__ == "__main__":
    main()
