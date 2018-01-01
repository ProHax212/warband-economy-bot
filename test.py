import cv2
import time
import sys

import numpy as np

from pytesseract import image_to_string
from PIL import Image
from PIL import ImageGrab

edge_detection_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
outline_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
tophat_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))

lower_name_rgb = np.array([82, 90, 95], dtype="uint8")
upper_name_rgb = np.array([213, 226, 238], dtype="uint8")

lower_price_rgb = np.array([21, 56, 60], dtype="uint8")
upper_price_rgb = np.array([66, 252, 255], dtype="uint8")

lower_price_gray = 140
upper_price_gray = 255

img = cv2.imread("test.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_sharpen = cv2.filter2D(gray, -1, sharpen_kernel)

edge = cv2.filter2D(img, -1, edge_detection_kernel)
sharpen = cv2.filter2D(img, -1, sharpen_kernel)
outline = cv2.filter2D(img, -1, outline_kernel)
edge_sharpen = cv2.filter2D(edge, -1, sharpen_kernel)
sharpen_edge = cv2.filter2D(sharpen, -1, sharpen_kernel)
tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, tophat_kernel)
tophat_sharpen = cv2.filter2D(tophat, -1, sharpen_kernel)

cv2.imwrite("edge.png", edge)
cv2.imwrite("sharpen.png", sharpen)
cv2.imwrite("edge_sharpen.png", edge_sharpen)
cv2.imwrite("sharpen_edge.png", sharpen_edge)
cv2.imwrite("outline.png", outline)
cv2.imwrite("tophat.png", tophat)
cv2.imwrite("tophat_sharpen.png", tophat_sharpen)
cv2.imwrite("gray_sharpen.png", gray_sharpen)

ret, maskPrice = cv2.threshold(gray_sharpen, lower_price_gray, upper_price_gray, cv2.THRESH_BINARY_INV)
cv2.imwrite("th1.png", maskPrice)

blur = cv2.GaussianBlur(gray_sharpen, (5, 5), 0)
ret, maskPrice = cv2.threshold(gray_sharpen, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
maskPrice = cv2.bitwise_not(maskPrice)
cv2.imwrite("th2.png", maskPrice)

gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
gray = cv2.blur(gray, (2, 2))
th3 = cv2.bitwise_not(gray)
cv2.imwrite("th3.png", th3)

print(image_to_string(Image.open("th1.png"), None, False))
print('-----------------------------')
print(image_to_string(Image.open("th2.png"), None, False))
