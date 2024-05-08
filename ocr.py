from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

import os
import time
import statistics

subscription_key = os.environ["VISION_KEY"]
endpoint = os.environ["VISION_ENDPOINT"]

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Function to read text from a local image and return lines of text
def get_text_lines(image_path):
    # Function to calculate the center of a bounding box
    def calculate_center(bbox):
        x_coords = bbox[::2]  # All X coordinates
        y_coords = bbox[1::2]  # All Y coordinates
        center_x = sum(x_coords) / len(x_coords)  # Average X coordinate
        center_y = sum(y_coords) / len(x_coords)  # Average Y coordinate
        return center_x, center_y

    # Function to calculate the height of a bounding box
    def calculate_height(bbox):
        y_coords = sorted(bbox[1::2])  # All Y coordinates sorted
        return y_coords[-1] - y_coords[0]  # Height of the bounding box
    
    with open(image_path, "rb") as image_stream:
        read_response = computervision_client.read_in_stream(image_stream, raw=True)

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # Wait for the OCR operation to complete
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(5)

    lines = []

    if read_result.status == OperationStatusCodes.succeeded:
        heights = []  # Bboxes height list
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                center_x, center_y = calculate_center(line.bounding_box)  # Calculate center
                height = calculate_height(line.bounding_box)  # Calculate height
                lines.append((center_y, center_x, line.text))
                heights.append(height)

        # Mean height calculation and setting tolerance for half of it
        if heights:
            average_height = statistics.mean(heights)
            tolerance = average_height / 2  # Tolerance based on half the average height
        
        # Sort by Y and then by X
        lines.sort(key=lambda x: (x[0], x[1]))  # First by Y, then by X

        # Group with calculated tolerance
        current_y = None
        current_line = []
        result_lines = []

        for y_coord, x_coord, text in lines:
            if current_y is None or abs(y_coord - current_y) > tolerance:
                if current_line:
                    # Save the complete line to the result
                    result_lines.append(" ".join([t[1] for t in sorted(current_line, key=lambda x: x[0])]))
                    current_line = []
                current_y = y_coord
            
            current_line.append((x_coord, text))

        # Save the last line to the result
        if current_line:
            current_line.sort(key=lambda x: x[0])
            result_lines.append(" ".join([t[1] for t in current_line]))

        return result_lines  # Return the text lines
    else:
        return "OCR Error"