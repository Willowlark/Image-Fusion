from __future__ import division
from PIL import Image
import os
from pprint import pprint
import numpy

class pixel_height_finder():

    def __init__(self, color):
        self.color = color

    def color_separator(self, im):
        if im.getpalette():
            im = im.convert('RGB')

        colors = im.getcolors()
        width, height = im.size
        colors_dict = dict((val[1],Image.new('RGB', (width, height), (0,0,0)))
                            for val in colors)
        pix = im.load()
        for i in xrange(width):
            for j in xrange(height):
                colors_dict[pix[i,j]].putpixel((i,j), pix[i,j])
        return colors_dict

    def find_height(self, infile):

        # im = Image.open(infile)
        colors_dict = self.color_separator(infile)
        # pprint(colors_dict)
        out = colors_dict[self.color]
        out.show()

        pixels = list(out.getdata())
        width, height = infile.size
        pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

        first = next(row for row in pixels if row.__contains__(self.color))
        top = pixels.index(first)
        print "first @ ln", top

        pixels.reverse()
        last = next(row for row in pixels if row.__contains__(self.color))
        bot = pixels.index(last)
        print "last @ ln", bot

        return bot- top, (bot - top) / height

    def pixel_write(self,infile):
        # this wil be replaced by the results of the operations of image merging and highlighting

        directory = os.path.dirname(os.path.realpath(__file__))
        temp = os.path.join(directory, 'Input', 'temp.jpg')
        im = Image.open(infile).convert("L")
        im.save(temp)
        im = Image.open(temp).convert("RGB")
        os.remove(temp)
        pixels = im.load()  # create the pixel map

        for i in range(127, 161):
            for j in range(132, 134):
                pixels[i, j] = self.color

        return im

if __name__ == '__main__':
    red = (249, 24, 0)
    phf = pixel_height_finder(red)

    directory = os.path.dirname(os.path.realpath(__file__))
    infile = os.path.join(directory, 'Input', 'IMG_0942.jpg')

    out = phf.pixel_write(infile).rotate(-90)
    out.show()
    print phf.find_height(out)
