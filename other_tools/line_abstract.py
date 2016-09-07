import cv2
from matplotlib import pyplot as plt
import PIL, os
from PIL import Image
from PIL import ImageFilter

def non_open_cv_method():
    img_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'Two Infrared test.png')
    img_path_2 = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'Two Crop test.png')

    image = PIL.Image.open(img_path)
    image = image.filter(ImageFilter.FIND_EDGES)
    image.show()
    image.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'Two Infrared test.png'))

    image = PIL.Image.open(img_path_2)
    image = image.filter(ImageFilter.FIND_EDGES)
    image.show()
    image.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'Two Crop test.png'))

def open_cv_method():

    img = cv2.imread('Input/Two Infrared.jpg')

    edges = cv2.Canny(img, 50, 250, apertureSize = 3)

    im = Image.fromarray(edges)
    im.show()
    im.save('Output/dump.png')

def test_open_cv():

    img = cv2.imread('Input/Two Infrared.jpg')

    image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnt = contours[4]

    img = cv2.drawContours(img, [cnt], 0, (0, 255, 0), 3)