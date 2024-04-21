import matplotlib.pyplot as plt
import cv2
import pytesseract

def plot_rgb(image):
    plt.figure(figsize=(16, 10))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def plot_gray(image):
    plt.figure(figsize=(16, 10))
    plt.imshow(image, cmap='Greys_r')
    plt.axis('off')
    plt.show()

def plot_ocr_boxes(processed_image, restored_contrast):
    d = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
    n_boxes = len(d['level'])
    boxes = cv2.cvtColor(restored_contrast.copy(), cv2.COLOR_BGR2RGB)
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
        boxes = cv2.rectangle(boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
    plot_rgb(boxes)