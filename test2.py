import cv2
import sys
from PIL import Image
from pytesseract import image_to_string

import numpy as np

file_name = "test.png"

name_lower = 227
name_upper = 227

price_lower = 175
price_upper = 176

name_rgb = np.array([208, 224, 240])
price_rgb = np.array([51, 187, 204])

sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

img = cv2.imread(file_name)
img_height, img_width, _ = img.shape
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_sharpened = cv2.filter2D(gray, -1, sharpen_kernel)
cv2.imwrite("gray.png", gray)
cv2.imwrite("gray_sharpened.png", gray_sharpened)

#ret, nameMask = cv2.threshold(gray, name_lower, name_upper, cv2.THRESH_BINARY)
nameMask = cv2.inRange(img, name_rgb, name_rgb)
#ret, priceMask = cv2.threshold(gray, price_lower, price_upper, cv2.THRESH_BINARY)
priceMask = cv2.inRange(img, price_rgb, price_rgb)

cv2.imwrite("nameMask.png", nameMask)
cv2.imwrite("priceMask.png", priceMask)

kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
numIterations = 1
nameDilated = cv2.dilate(nameMask, kernel, iterations=numIterations)
priceDilated = cv2.dilate(priceMask, kernel, iterations=numIterations)
cv2.imwrite("priceDilated.png", priceDilated)
cv2.imwrite("nameDilated.png", nameDilated)

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

main_contour = np.array(point_list).reshape(-1, 1, 2).astype(np.int32)
[x, y, w, h] = cv2.boundingRect(cv2.convexHull(main_contour, returnPoints=True))

roi = gray.copy()[y:y+h, x:x+w]
blur = cv2.GaussianBlur(roi, (5, 5), 0)
ret, th1 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite("temp.png", th1)
print(image_to_string(Image.open("temp.png")))

cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 255), 2)

cv2.imshow('captcha_result', img_copy)
cv2.waitKey()
