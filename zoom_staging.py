from __future__ import division
from PIL import Image, ImageDraw
import os, cv2, sys, numpy

def make_zoomed(img, zoom_factor, x_offset, y_offset, out=None,):

    im = Image.open(img)
    crop = im.crop((x_offset, y_offset, (im.size[0] / zoom_factor) + x_offset, (im.size[1] / zoom_factor) + y_offset))
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

def apply_border(img, points, color=(255,0,0), border=3, out=None):

    if out is None:
        im = img.copy()
    else:
        im = img
    draw = ImageDraw.Draw(im)

    shifted = points[1:] + points[:1]
    lis = zip(points, shifted)

    for pair in lis:
        draw.line((pair[0][0], pair[0][1], pair[1][0], pair[1][1]), fill=color, width=border)

    return im

class location_finder:

    def __init__(self, tot_img, sub_img, minimum_precision=0.89, strat=None,):

        if strat:
            self.strat = strat
        else:
            sys.stderr.write("Warning, no strategy assigned")
        self.tot_img = tot_img
        self.sub_img = sub_img
        self.minimum_precision = minimum_precision
        self.sub_pix = self.sub_img.load()
        self.tot_pix = self.tot_img.load()

    def exe(self, width_lim, height_lim):

        lim_matches = (self.sub_img.size[0] * 2) + (self.sub_img.size[1] * 2)

        for i in range(1, width_lim):
            for j in range(1, height_lim):
                cur_matches = self.strat(self, col=i, row=j)
                result_ratio = cur_matches / lim_matches
                if result_ratio >= self.minimum_precision:
                    print "match found!", cur_matches, " at ", i, j
                    return cur_matches, lim_matches, result_ratio, i, j
            sys.stdout.write('.')
            sys.stdout.flush()
        print "\n"

    def border_check(self, col=0, row=0):

        matches = 0
        for i in range(self.sub_img.size[0]):
            if self.sub_pix[i, 0] == self.tot_pix[i + col, 0 + row]:
                matches += 1
        for j in range(self.sub_img.size[1]):
            if self.sub_pix[0, j] == self.tot_pix[0 + col, j + row]:
                matches += 1
        for i in range(self.sub_img.size[0]):
            if self.sub_pix[i, self.sub_img.size[1] - 1] == self.tot_pix[i + col, 0 + row]:
                matches += 1
        for j in range(self.sub_img.size[1]):
            if self.sub_pix[self.sub_img.size[0] - 1, j] == self.tot_pix[0 + col, j + row]:
                matches += 1

        return matches

    def exhaust_check(self, col=0, row=0):

        matches = 0
        for i in range(self.sub_img.size[0]):
            for j in range(self.sub_img.size[1]):
                if self.sub_pix[i, j] == self.tot_pix[i + col, j + row]:
                    matches += 1

        return matches

def show_and_wait(file):

    if isinstance(file, basestring):
        img = cv2.imread(file)
    else:
        img = numpy.array(file)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main(zoom_factor, minimum_precision, verbose=False, x_offset=0, y_offset=0):

    print "Trying Degree of Precision", minimum_precision * 100

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')
    out_sub_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_sub.jpg')
    out_tot_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_tot.jpg')

    #
    # staging testing
    #
    zoomed = make_zoomed(inp_file, zoom_factor, x_offset=x_offset, y_offset=y_offset)
    if verbose:
        show_and_wait(zoomed)

    #
    # Un-packing image to be used in overlay
    #
    img = Image.open(inp_file)
    img_lines = generate_lines(img)
    img_lines.save(out_tot_file)

    #
    # prepare the sub_img by first un_zooming, then applying generate lines, then cropping to fit image
    #
    un_zoomed = zoomed.crop((0,0, zoomed.size[0] * zoom_factor, zoomed.size[1] * zoom_factor)).resize(img.size, Image.ANTIALIAS)

    #
    # Check for inappropriate x / y offset
    if x_offset > img.size[0] / zoom_factor or y_offset > img.size[1] / zoom_factor:
        string = "Error, x_offset and y_offset with the sub_img width cannot exceed the size of th e tot_img"
        string += "\noffsets (x, y): " + str(x_offset) + ", " + str(y_offset)
        string += "\ntot img crop lim: " + str(img.size[0] / zoom_factor) + ", " + str(img.size[1] / zoom_factor)
        raise AssertionError(string)

    if verbose:
        show_and_wait(un_zoomed)
    un_zoomed_lines = generate_lines(un_zoomed)
    if verbose:
        show_and_wait(un_zoomed_lines)
    un_zoomed_lines_crop = un_zoomed_lines.crop((1, 1, (un_zoomed.size[0] / zoom_factor)-1, (un_zoomed.size[1] / zoom_factor)-1))
    if verbose:
        show_and_wait(un_zoomed_lines_crop)
    un_zoomed_lines_crop.save(out_sub_file)

    #
    # Use loc_finder to solve for location
    #
    width_lim = img_lines.size[0] - un_zoomed_lines_crop.size[0]
    height_lim = img_lines.size[1] - un_zoomed_lines_crop.size[1]

    try:
        loc_find = location_finder(tot_img=img_lines, sub_img=un_zoomed_lines_crop, minimum_precision=minimum_precision, strat=location_finder.border_check)
        current_matches, max_matches, result_matches, x, y = loc_find.exe(width_lim, height_lim)
    except Exception as e:
        raise Exception("Degree of Precision " + str(minimum_precision) + " failed")

    print "Succeeded", "number of matches:", current_matches, "of", max_matches, ":", result_matches

    x, y = x-1, y-1 # NOTE at location of x-1, y-1 as we needed to shave this border of the lines photo for erroneous line recognition at the border fo the crop

    print "imaged sourced to", x, y

    #
    # overlay image for visual
    #
    img.paste(un_zoomed.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x,y))
    img.show()

    img_lines.paste(un_zoomed_lines.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x,y))
    img_lines.show()

    sub_w = un_zoomed.size[0] / zoom_factor
    sub_h = un_zoomed.size[1] / zoom_factor
    highlighted = apply_border(img, points=[(x, y), (x, sub_h+y), (sub_w+x, sub_h+y), (sub_w+x, y)], border=1)
    highlighted.show()

def img_explore(x_offset, y_offset):

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')

    img = Image.open(inp_file)
    zoomed = make_zoomed(inp_file, 2.0, x_offset, y_offset)

    un_zoomed = zoomed.crop((0, 0, zoomed.size[0] * 2.0, zoomed.size[1] * 2.0)).resize(img.size,Image.ANTIALIAS)
    un_zoomed_crop = un_zoomed.crop(
        (1, 1, (un_zoomed.size[0] / 2.0) - 1, (un_zoomed.size[1] / 2.0) - 1))

    sub_w = un_zoomed.size[0] / 2.0
    sub_h = un_zoomed.size[1] / 2.0
    highlighted = apply_border(un_zoomed, points=[(x_offset, y_offset), (x_offset, sub_h + y_offset), (sub_w + x_offset, sub_h + y_offset), (sub_w + x_offset, y_offset)], border=1)
    highlighted.show()

    print "h", un_zoomed_crop.size[1], "w", un_zoomed_crop.size[0]

if __name__ == '__main__':

    debug = 0

    ar = numpy.arange(0.91, 0.85, -0.01)

    if not debug:
        x_offset, y_offset = 0, 0
    else:
        x_offset, y_offset = 250, 250

    for pct in ar:
        try:
            main(zoom_factor=2.0, minimum_precision=pct, x_offset=x_offset, y_offset=y_offset)
            sys.exit(0)
        except AssertionError as e:
            print e
            break
        except Exception as e:
            print e
    sys.stderr.write("IMAGE NOT FOUND\n")
    sys.exit(-1)

    # img_explore(0, 0)

