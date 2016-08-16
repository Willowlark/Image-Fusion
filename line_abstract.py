import cv2
from matplotlib import pyplot as plt
import PIL, os
from PIL import Image
from PIL import ImageFilter

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

# img = cv2.imread('Input/Two Infrared.jpg')
# edges = cv2.Canny(img,50,200,apertureSize = 3)
#
# plt.subplot(121),plt.imshow(img,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
#
# plt.show()