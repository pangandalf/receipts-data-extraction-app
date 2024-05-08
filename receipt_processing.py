import ocr
import logging
import os

from ocr_to_json import *

# function for using yolo model with ocr and returning structured data
def receipt_extraction(image_path):
    logging.basicConfig(level=logging.ERROR)

    copy_image_path = "tmp.jpg"

    with open(image_path, "rb") as original_file:
        file_content = original_file.read()

    with open(copy_image_path, "wb") as copy_file:
        copy_file.write(file_content)

    image_path = copy_image_path

    try:
        import detect_script
        detect_script.detect_image(image_path)
        detect_folder_path = os.path.join(".", "yolov9", "runs", "detect", "exp", "crops")
        logo_path = os.path.join(detect_folder_path, "logo", image_path)
        products_path = os.path.join(detect_folder_path, "products", image_path)
        logo = ocr.get_text_lines(logo_path)
        products = ocr.get_text_lines(products_path)
        detect_script.clear_detect_folder()
        os.remove(image_path)
    except Exception as e:
        os.remove(image_path)
        logging.error(f"Sorry, problem with OCR or ml model ocurred. {e}")

    print(products)
    try:
        store_name = get_store_name(logo)
        date = get_date()
        data = get_products(products)
        data = clear_data(data)
    
    except Exception as e:
        logging.error(f"Sorry, extraction could not have been performed. {e}")
        store_name = ''
        date = ''
        data = ''
    
    return store_name, date, data