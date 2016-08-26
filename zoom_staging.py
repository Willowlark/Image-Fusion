from __future__ import division
from PIL import Image, ImageDraw
import os, cv2, sys, numpy

def make_zoomed(img, zoom_factor, out=None, x_offset=0, y_offset=0):

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

        max_matches = (self.sub_img.size[0] * 2) + (self.sub_img.size[1] * 2)
        print "max matches", max_matches

        for i in range(1, width_lim):
            for j in range(1, height_lim):
                cur_matches = self.strat(self, col=i, row=j)
                result_ratio = cur_matches / max_matches
                if result_ratio >= self.minimum_precision:
                    print "match found!", cur_matches, " at ", i, j
                    return cur_matches, max_matches, result_ratio, i, j

        # lis = []
        # for i in range(0, width_lim):
        #     for j in range(0, height_lim):
        #         res = self.strat(self, col=i, row=j)
        #         lis.append((res, i, j))
        #
        # lis.sort(key=lambda tup: tup[0], reverse=True)
        # return lis[0][0], lis[0][1], lis[0][2]

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

def main(zoom_factor):

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')
    out_sub_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_sub.jpg')
    out_tot_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_tot.jpg')

    #
    # staging testing
    #
    zoomed = make_zoomed(inp_file, zoom_factor)
    #zoomed.show()

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
    # un_zoomed.show()
    un_zoomed_lines = generate_lines(un_zoomed)
    # un_zoomed_lines.show()
    un_zoomed_lines_crop = un_zoomed_lines.crop((1, 1, (un_zoomed.size[0] / zoom_factor)-1, (un_zoomed.size[1] / zoom_factor)-1))
    # un_zoomed_crop.show()
    un_zoomed_lines_crop.save(out_sub_file)

    #
    # Use loc_finder to solve for location
    #
    width_lim = img_lines.size[0] - un_zoomed_lines_crop.size[0]
    height_lim = img_lines.size[1] - un_zoomed_lines_crop.size[1]

    loc_find = location_finder(tot_img=img_lines, sub_img=un_zoomed_lines_crop, strat=location_finder.border_check)
    current_matches, max_matches, result_matches, x, y = loc_find.exe(width_lim, height_lim)

    print "Succeeded", "number of matches:", current_matches, "of", max_matches, ":", result_matches
    print "imaged sourced at", x-1, y-1

    #
    # overlay image for visual
    # NOTE at location of x-1, y-1 as we needed to shave this border of the lines photo for erroneous line recognition at the border fo the crop
    #
    img.paste(un_zoomed.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x-1,y-1))
    img.show()

    img_lines.paste(un_zoomed_lines.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x-1,y-1))
    img_lines.show()

    sub_w = un_zoomed.size[0] / zoom_factor
    sub_h = un_zoomed.size[1] / zoom_factor
    highlighted = apply_border(img, points=[(0, 0), (0, sub_h), (sub_w, sub_h), (sub_w, 0)], border=1)
    highlighted.show()

def img_explore():

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')

    img = Image.open(inp_file)
    zoomed = make_zoomed(inp_file, 2.0)

    un_zoomed = zoomed.crop((0, 0, zoomed.size[0] * 2.0, zoomed.size[1] * 2.0)).resize(img.size,
                                                                                                       Image.ANTIALIAS)
    un_zoomed_crop = un_zoomed.crop(
        (1, 1, (un_zoomed.size[0] / 2.0) - 1, (un_zoomed.size[1] / 2.0) - 1))

    un_zoomed_crop.show()

    print "h", un_zoomed_crop.size[1], "w", un_zoomed_crop.size[0]

if __name__ == '__main__':

    main(zoom_factor=2.0)
    #img_explore()

    sys.exit(0)