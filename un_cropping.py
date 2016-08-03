from __future__ import division
from PIL import Image, ImageOps, ImageFilter
import os, sys, time
from pprint import pprint

class un_crop():

    def __init__(self):
        pass

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
        # out.show()

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

def find_loc_double_check(original, img):

    pixels = list(img.getdata())
    width, height = img.size
    img_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    # pprint(img_pixels)

    pixels = list(original.getdata())
    width, height = original.size
    orig_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    # pprint(orig_pixels)

    first_row_img = img_pixels[0]
    last_row_img = img_pixels[-1]

    row_top = 0
    col_top = 0
    for row_orig in orig_pixels:
        col_top = sublistExists(row_orig, first_row_img)
        if col_top > 0:
            break
        row_top +=1

    row_bot = 0
    col_bot = 0
    for row_orig in orig_pixels:
        col_bot = sublistExists(row_orig, last_row_img)
        if col_bot > 0:
            break
        row_bot += 1

    if row_bot - row_top == len(img_pixels)-1:
        return row_top, col_top
    else:
        return ()

def find_loc_single_check(original, img):

    pixels = list(img.getdata())
    width, height = img.size
    img_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    # pprint(img_pixels)

    pixels = list(original.getdata())
    width, height = original.size
    orig_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    # pprint(orig_pixels)

    first_row_img = img_pixels[0]

    row_top = 0
    col_top = 0
    for row_orig in orig_pixels:
        col_top = sublistExists(row_orig, first_row_img)
        if col_top > 0:
            break
        row_top +=1

    return row_top, col_top

def sublistExists(list, sublist):
    for i in range(len(list)-len(sublist)+1):
        if sublist == list[i:i+len(sublist)]:
            return i
    return -1

def rot_list(list):
    ret = []
    width = len(list[0])
    for i in xrange(0, width):
        col = []
        for row in list:
            col.append(row[i])
        ret.append(col)
    return ret

def my_rot(img):
    # orig is image that is being rotated
    pixels = list(img.getdata())
    width, height = img.size
    img_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    rotated = rot_list(img_pixels)
    flattened = [item for sublist in rotated for item in sublist]

    ret = Image.new("RGBA", (width, height))
    ret.putdata(flattened[::-1])
    return ret

def place_image(img, new_img, orig):

    img_w, img_h = img.size
    new_w, new_h = new_img.size
    offset = (img_w - new_w, img_h - new_h)
    img_with_border = ImageOps.expand(img, border=1, fill='red')
    orig_with_bars = orig.crop((0 - offset[0], 0 - offset[1], orig.size[0] + offset[0], orig.size[1] + offset[1]))
    orig_with_bars.paste(img_with_border, loc)
    return orig_with_bars

if __name__ == '__main__':

    start_time = time.time()

    tests = []
    index = ()

    img = Image.open('Input/Two Crop test.png')
    #img = img.filter(ImageFilter.FIND_EDGES)
    orig = Image.open('Input/Two Infrared test.png')
    #orig = orig.filter(ImageFilter.FIND_EDGES)

    # orig = ImageOps.expand(Image.open('Input/Two Infrared.png'), border=max(img.size), fill='black')
    # orig = orig.crop((-1*img.size[0], -1*img.size[1], orig.size[0]+img.size[0], orig.size[1]+img.size[1]))

    first = (orig, img)

    tests.append(first)

    # top row
    for i in xrange(0, int(img.size[0]*.80)):
        new_img = img.crop((i, 0, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    # left column
    img = my_rot(img)
    orig = my_rot(orig)
    for i in xrange(0, int(img.size[1]*.80)):
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    # bottom row
    img = my_rot(my_rot(img))
    orig = my_rot(my_rot(orig))
    for i in xrange(0, int(img.size[1] * .80)):
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    # right col
    img = my_rot(my_rot(my_rot(img)))
    orig = my_rot(my_rot(my_rot(orig)))
    for i in xrange(0, int(img.size[1] * .80)):
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    for entry in tests:
        loc = find_loc_double_check(*entry)
        if loc:
            print entry[1].info, "Found in", entry[0].info
            img = Image.open('Input/Two Crop test.png')
            res = place_image(img, entry[1], entry[0])
            res.show()
            break
            # raw_input("Press Enter to continue...")
        else:
            sys.stdout.write('.')
            sys.stdout.flush()

    print("\n--- %s seconds ---" % (time.time() - start_time))
    sys.exit(0)


