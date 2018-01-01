import cv2
import sys
from PIL import Image
from pytesseract import image_to_string

import numpy as np

file_name = "test.png"

name_lower = 227
name_upper = 227

price_lower = 176
price_upper = 176

scale_lower = 254
scale_upper = 254

name_rgb = np.array([208, 224, 240])
price_rgb = np.array([51, 187, 204])
scale_rgb = np.array([254, 254, 254])

sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
kernel = np.ones((5, 5), np.uint8)

img = cv2.imread(file_name)
img_height, img_width, _ = img.shape
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
cv2.imwrite("gray.png", gray)
cv2.imwrite("gray_sharpened.png", gray_sharpened)

nameMask = cv2.inRange(img, name_rgb, name_rgb)
priceMask = cv2.inRange(img, price_rgb, price_rgb)
scaleMask = cv2.inRange(img, scale_rgb, scale_rgb)

cv2.imwrite("nameMask.png", nameMask)
cv2.imwrite("priceMask.png", priceMask)
cv2.imwrite("scaleMask.png", scaleMask)

# Close scaleMask
close_kernel = np.ones((5, 5), np.uint8)
erode_kernel = np.ones((2, 2), np.uint8)
scaleMask = cv2.erode(cv2.dilate(scaleMask, close_kernel, iterations=1), close_kernel, iterations=1)
cv2.imwrite("scaleMaskClosed.png", scaleMask)

# Erode scaleMask
scaleMaskEroded = cv2.erode(scaleMask, erode_kernel, iterations = 1)
cv2.imwrite("scaleMaskEroded.png", scaleMaskEroded)

kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
numIterations = 1
nameDilated = cv2.dilate(nameMask, kernel, iterations=numIterations)
priceDilated = cv2.dilate(priceMask, kernel, iterations=numIterations)
scaleDilated = cv2.dilate(scaleMaskEroded, kernel, iterations=numIterations)
cv2.imwrite("priceDilated.png", priceDilated)
cv2.imwrite("nameDilated.png", nameDilated)
cv2.imwrite("scaleDilated.png", scaleDilated)

# Get contours for the price
image, contoursPrice, hierarchy = cv2.findContours(priceDilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
img_copy = img.copy()
point_list = []
for contour in contoursPrice:
    for point in contour:
        point_list.append(point)

# Get contours for the name
image, contoursName, hierarchy = cv2.findContours(nameDilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for contour in contoursName:
    for point in contour:
        point_list.append(point)

# Get contours for the scale
image, contoursScale, hierarchy = cv2.findContours(scaleDilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
multiplier_point_list = []
for contour in contoursScale:
    for point in contour:
        multiplier_point_list.append(point)

# Multiplier contours
multiplier_contour = np.array(multiplier_point_list).reshape(-1, 1, 2).astype(np.int32)
[x, y, w, h] = cv2.boundingRect(cv2.convexHull(multiplier_contour, returnPoints=True))
roi = gray.copy()[y:y+h, x:x+w]
blur = cv2.GaussianBlur(roi, (5, 5), 0)
ret, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite("tempMultiplier.png", th1)
cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 255), 2)
print(image_to_string(Image.open("tempMultiplier.png")))

# Main contours
main_contour = np.array(point_list).reshape(-1, 1, 2).astype(np.int32)
[x, y, w, h] = cv2.boundingRect(cv2.convexHull(main_contour, returnPoints=True))
roi = gray.copy()[y:y+h, x:x+w]
blur = cv2.GaussianBlur(roi, (5, 5), 0)
ret, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite("temp.png", th1)
cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 255), 2)
print(image_to_string(Image.open("temp.png")))

cv2.imshow('captcha_result', img_copy)
cv2.waitKey()
