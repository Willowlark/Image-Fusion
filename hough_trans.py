import cv2, sys, os
import numpy as np
import PIL
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter, ImageSequence
import images2gif
from pprint import pprint
from Tkinter import *
from gif_player import gifPlayer
import pyglet

#https://pypi.python.org/pypi/images2gif

# image = Image.open('Input/Two Infrared test.png')
# image = image.filter(ImageFilter.FIND_EDGES)
# image.show()
#
# image = Image.open('Input/Two Crop test.png')
# image = image.filter(ImageFilter.FIND_EDGES)
# image.show()

# img = cv2.imread('Input/Two Infrared.jpg')
# edges = cv2.Canny(img,50,200,apertureSize = 3)
#
# plt.subplot(121),plt.imshow(img,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
#
# plt.show()

if __name__ == '__main__' :

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    # img = Image.open('Input/IMG_0993.jpg')
    # img.save('Input/IMG_0993.png')
    #
    # img = Image.open('Input/IMG_1004.jpg')
    # img.save('Input/IMG_1004.png')

    # Read source image.
    im_src = cv2.imread('Input/IMG_1004.png')
    # Four corners of the book in source image
    pts_src = np.array([[1623,1149], [1623,1405],[2282,1149],[2282,1405]])


    # Read destination image.
    im_dst = cv2.imread('Input/IMG_0993.png')
    # Four corners of the book in destination image.
    pts_dst = np.array([[179,196], [179,205], [198,196], [198,205]])

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1],im_dst.shape[0]))

    cv2.imwrite('gif_test/frame2.png', im_out)



    im_dst = cv2.imread('Input/IMG_0991.png')
    # Four corners of the book in destination image.
    pts_dst = np.array([[116, 155], [116, 125], [179, 155], [179, 125]])
    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)
    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite('gif_test/frame3.png', im_out)


    frames = []

    file_names = sorted(('gif_test/' + fn for fn in os.listdir('C:\Users\Bob S\PycharmProjects\Image-Fusion\gif_test') if fn.endswith('.png')))
    pprint(file_names)

    cv2.waitKey(0)

    images = [PIL.Image.open(fn) for fn in file_names]

    filename = 'gif_test/my_gif.GIF'
    images2gif.writeGif(filename, images, duration=0.5)

    root = Tk()
    anim = gifPlayer(root, 'gif_test/my_gif.gif')
    anim.pack()
    anim.run(root)



