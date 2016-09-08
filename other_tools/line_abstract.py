import cv2
from matplotlib import pyplot as plt
import PIL, os
from PIL import Image
from PIL import ImageFilter
from Merging.ImageMerge import *
from Merging.PixelProcess import *
import Console

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
     # im.show()
    im.save('Output/dump.png')

def test_open_cv():

    inp1_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'dump.jpg')
    inp2_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'black.jpg')

    img = cv2.imread('Input/Two Infrared.jpg')

    edges = cv2.Canny(img, 50, 250, apertureSize=3)

    im = Image.fromarray(edges)
    im = im.convert("RGB")
    im.save(inp1_file)

    temp = Image.open(inp1_file)

    img2 = Image.new("RGBA", temp.size)
    img2.save(inp2_file)

    consolas = Console.Console(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'ImF.jpg'))
    consolas.do_extractremote(None)
    consolas.do_redhighlight(None)
    consolas.do_colordiff(120)

    consolas.do_merge(inp1_file)
    consolas.do_merge(inp2_file)

    consolas.do_gengroups(None)
    consolas.do_countsortgroups(None)
    f = consolas.groups.first()
    print f

if __name__ == '__main__':

    test_open_cv()

