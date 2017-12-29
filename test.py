import cv2
import time
import sys

import numpy as np

from pytesseract import image_to_string
from PIL import Image
from PIL import ImageGrab

edge_detection_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

img = cv2.imread("test.png")

edge = cv2.filter2D(img, -1, edge_detection_kernel)
sharpen = cv2.filter2D(img, -1, sharpen_kernel)
edge_sharpen = cv2.filter2D(edge, -1, sharpen_kernel)
sharpen_edge = cv2.filter2D(sharpen, -1, sharpen_kernel)

cv2.imwrite("edge.png", edge)
cv2.imwrite("sharpen.png", sharpen)
cv2.imwrite("edge_sharpen.png", edge_sharpen)
cv2.imwrite("sharpen_edge.png", sharpen_edge)
sys.exit(0)

print(image_to_string(Image.open("th1.png")))
print('-------------------------------')
print(image_to_string(Image.open("th2.png")))

img = cv2.imread('./test.png', cv2.IMREAD_UNCHANGED)

lower_name_rgb = np.array([82, 90, 95], dtype="uint8")
upper_name_rgb = np.array([213, 226, 238], dtype="uint8")

lower_price_rgb = np.array([26, 78, 85], dtype="uint8")
upper_price_rgb = np.array([50, 181, 198], dtype="uint8")

maskName = cv2.inRange(img, lower_name_rgb, upper_name_rgb)
maskPrice = cv2.inRange(img, lower_price_rgb, upper_price_rgb)

cv2.imwrite("th1.png", maskName)
cv2.imwrite("th2.png", maskPrice)


#blur = cv2.GaussianBlur(img, (5, 5), 0)

#stepIncrement = 40

#threshold = 0
#while threshold <= 255:
#    ret1, th1 = cv2.threshold(blur, threshold, min(255, threshold + stepIncrement), cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#    cv2.imwrite("th1.png", th1)
#    print('---------------------------------------------')
#    print(image_to_string(Image.open("th1.png")))
#    threshold += stepIncrement

#ImageGrab.grab().save('screen_capture.jpg', 'JPEG')
