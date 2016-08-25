from __future__ import division
from PIL import Image, ImageOps
import os, cv2, sys, numpy


def get_zoomed(img, zoom_factor, out=None):

    im = Image.open(img)
    crop = im.crop((0, 0, im.size[0] / zoom_factor, im.size[1] / zoom_factor))
    res = crop.resize(im.size, Image.ANTIALIAS)
    if out is None:
        return res
    res.save(out)

def generate_lines(inp, out=None):

    if isinstance(inp, basestring):
        edges = cv2.Canny(cv2.imread(inp), 50, 250, apertureSize=3)
    else:
        edges = cv2.Canny(numpy.array(inp), 50, 250, apertureSize=3)
    im = Image.fromarray(edges)
    im = im.convert("RGB")
    if out is None:
        return im
    im.save(out)

def touch_up(inp, out=None):

    if isinstance(inp, basestring):
        img = Image.open(inp)
    else:
        img = inp

    return ImageOps.colorize(img.convert('L'), (0,0,0), (255,255,255))

def main(zoom_factor):

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')
    out_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result.jpg')

    # staging testing
    zoomed = get_zoomed(inp_file, zoom_factor)
    lines_zoomed = generate_lines(zoomed)
    lines_zoomed.save(out_file)

    # Un-packing image to be used in overlay
    img = generate_lines(Image.open(inp_file))
    un_zoomed = lines_zoomed.crop((0,0, zoomed.size[0] * zoom_factor, zoomed.size[1] * zoom_factor)).resize(img.size, Image.ANTIALIAS)

    # overlay image for visual
    img.paste(un_zoomed.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (0,0))
    img.show()
    img.save(out_file)

    img = touch_up(img)
    img.show()

if __name__ == '__main__':

    main(zoom_factor=2.0)

    sys.exit(0)