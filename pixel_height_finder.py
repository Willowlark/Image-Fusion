from __future__ import division
from PIL import Image
import os
from pprint import pprint
import numpy

red = (249, 24, 0)

def color_separator(im):
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

directory = os.path.dirname(os.path.realpath(__file__))
infile = directory + '\\Input\\OdEct.png'

im = Image.open(infile)
colors_dict = color_separator(im)
# pprint(colors_dict)
out = colors_dict[red]
# out.show()

pixels = list(out.getdata())
width, height = im.size
pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

first = next(row for row in pixels if row.__contains__(red))
top = pixels.index(first)
print "first @", top

last = next(row for row in pixels[::-1] if row.__contains__(red))
bot = pixels.index(last)
print "last @", bot

print "Height: ", bot- top
print "px %: ", (bot - top) / height
