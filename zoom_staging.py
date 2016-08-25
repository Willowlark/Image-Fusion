from __future__ import division
from PIL import Image, ImageOps, ImageDraw
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

def find_loc(tot_img, sub_img, col=0, row=0):

    sub_pix = sub_img.load()
    tot_pix = tot_img.load()

    matches = 0

    # border check
    for i in range (sub_img.size[0]):
        if sub_pix[i, 0] == tot_pix[i + col, 0 + row]:
            matches += 1
    for j in range(sub_img.size[1]):
        if sub_pix[0, j] == tot_pix[0 + col, j + row]:
            matches += 1
    for i in range(sub_img.size[0]):
        if sub_pix[i, sub_img.size[1]-1] == tot_pix[i + col, 0 + row]:
            matches += 1
    for j in range(sub_img.size[1]):
        if sub_pix[sub_img.size[0]-1, j] == tot_pix[0 + col, j + row]:
            matches += 1

    # total check
    # for i in range(sub_img.size[0]):
    #     for j in range(sub_img.size[1]):
    #         if sub_pix[i, j] == tot_pix[i + col, j + row]:
    #             matches += 1

    return matches


def main(zoom_factor):

    inp_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'mt_mckinley.jpg')
    out_sub_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_sub.jpg')
    out_tot_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'result_tot.jpg')

    # staging testing
    zoomed = get_zoomed(inp_file, zoom_factor)
    # zoomed = generate_lines(zoomed)
    #zoomed.show()

    # Un-packing image to be used in overlay
    img = Image.open(inp_file)
    img_lines = generate_lines(img)
    img_lines.save(out_tot_file)

    un_zoomed = zoomed.crop((0,0, zoomed.size[0] * zoom_factor, zoomed.size[1] * zoom_factor)).resize(img.size, Image.ANTIALIAS)
    # un_zoomed.show()

    un_zoomed_lines = generate_lines(un_zoomed)
    # un_zoomed_lines.show()

    un_zoomed_crop = un_zoomed_lines.crop((0, 0, (un_zoomed.size[0] / zoom_factor)-1, (un_zoomed.size[1] / zoom_factor)-1))
    # un_zoomed_crop.show()
    un_zoomed_crop.save(out_sub_file)

    # img_lines.show()
    # un_zoomed_crop.show()

    width_lim = img_lines.size[0] - un_zoomed_crop.size[0]
    height_lim = img_lines.size[1] - un_zoomed_crop.size[1]

    lis = []
    for i in range(0, width_lim):
        for j in range(0, height_lim):
            res = find_loc(img_lines, un_zoomed_crop, col=i, row=j)
            lis.append((res, i, j))

    lis.sort(key=lambda tup: tup[0], reverse=True)
    matches, x, y = lis[0][0], lis[0][1], lis[0][2]

    print "Succeeded", "number of matches:", matches

    # overlay image for visual
    img.paste(un_zoomed.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x,y))
    img.show()

    img_lines.paste(un_zoomed_lines.crop((0, 0, un_zoomed.size[0] / zoom_factor, un_zoomed.size[1] / zoom_factor)), (x,y))
    img_lines.show()

    sub_w = un_zoomed.size[0] / zoom_factor
    sub_h = un_zoomed.size[1] / zoom_factor
    highlighted = apply_border(img, points=[(0, 0), (0, sub_h), (sub_w, sub_h), (sub_w, 0)], border=1)
    highlighted.show()

if __name__ == '__main__':

    main(zoom_factor=2.0)

    sys.exit(0)