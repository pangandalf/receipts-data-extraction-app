import subprocess

# script for using the ml model
def detect_image(image_path):
    command = [
        'python',
        'yolov9/detect.py',
        '--weights', 'best.onnx', # model file with onnx extension
        '--source', image_path,
        '--save-crop'
    ]

    try:
        subprocess.run(command, check=True)
        print(f'Detection completed for {image_path}')
    except subprocess.CalledProcessError as e:
        print(f"Error during detection: {e}")

import os
import shutil

# clearing detect folder
def clear_detect_folder():
    detect_folder_path = './yolov9/runs/detect'

    if os.path.exists(detect_folder_path):
        for item in os.listdir(detect_folder_path):
            item_path = os.path.join(detect_folder_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)