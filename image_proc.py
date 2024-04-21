import cv2

import perspective_fun as pf
import image_fun

def prepare_image(file_name):
    image = cv2.imread(file_name)
    resize_ratio = 500 / image.shape[0]
    original = image.copy()
    image = image_fun.opencv_resize(image, resize_ratio)
    image = image_fun.adjust_gamma(image, gamma=0.5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    return blurred, original, resize_ratio

def perspective_restoration(blurred, original, resize_ratio):
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilated = cv2.dilate(blurred, rectKernel)  # Dylatacja obrazu
    edged = cv2.Canny(dilated, 30, 150)  # Wykrywanie krawędzi metodą Canny'ego

    # Wykrywanie konturów
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Znalezienie największego konturu (najbardziej prawdopodobnego jako paragraf/kwit)
    receipt_contour = max(contours, key=cv2.contourArea)

    # Przybliżenie konturu
    epsilon = 0.1 * cv2.arcLength(receipt_contour, True)
    contour_approx = cv2.approxPolyDP(receipt_contour, epsilon, True)

    # Przywrócenie perspektywy
    perspective_rect = pf.contour_to_rect(contour_approx, resize_ratio)
    restored = pf.wrap_perspective(original.copy(), perspective_rect)

    # Kontrastowanie obrazu
    restored_contrast = image_fun.bw_scanner(restored)

    return restored, restored_contrast

def preprocess_image(image):
    # Usunięcie szumów za pomocą filtrowania medianowego
    denoised = cv2.medianBlur(image, 3)
    
    # Odszumianie i wyostrzanie obrazu
    denoised_sharpened = cv2.GaussianBlur(denoised, (3, 3), 0)
    sharpened = cv2.addWeighted(denoised, 1.5, denoised_sharpened, -0.5, 0)
    
    # Progowanie adaptacyjne z metodą MEAN_C
    threshold = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return threshold