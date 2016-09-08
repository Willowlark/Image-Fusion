from __future__ import division
from PIL import Image, ImageOps
import os, sys, time

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

def place_image(img, new_img, orig, loc, highlight=False):
    img_p = img
    if highlight:
        img_p = ImageOps.expand(img.crop((1,1,img.size[0]-1,img.size[1]-1)), border=1, fill='red')
    img_w, img_h = img_p.size
    new_w, new_h = new_img.size
    offset = ((img_w - new_w)+1, (img_h - new_h)+1)
    res = orig.crop((0 - offset[0], 0 - offset[1], orig.size[0] + offset[0], orig.size[1] + offset[1]))
    res.paste(img_p, loc)
    return res

def main(subimg, totimg):
    min_overlap_factor = 0.9
    tests = []
    first = (totimg, subimg)

    tests.append(first)

    # top row
    for i in xrange(0, int(subimg.size[0] * min_overlap_factor)):
        new_img = subimg.crop((i, 0, subimg.size[0], subimg.size[1]))
        tests.append((totimg, new_img))

    # left column
    img = subimg.rotate(90, resample=Image.BICUBIC, expand=True)
    orig = totimg.rotate(90, resample=Image.BICUBIC, expand=True)
    lis = xrange(0, int(img.size[1] * min_overlap_factor))
    for i in lis:
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    # bottom row
    img = subimg.rotate(180, resample=Image.BICUBIC, expand=True)
    orig = totimg.rotate(180, resample=Image.BICUBIC, expand=True)
    lis = xrange(0, int(img.size[1] * min_overlap_factor))
    for i in lis:
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    # right col
    img = subimg.rotate(270, resample=Image.BICUBIC, expand=True)
    orig = totimg.rotate(270, resample=Image.BICUBIC, expand=True)
    lis = xrange(0, int(img.size[1] * min_overlap_factor))
    for i in lis:
        new_img = img.crop((0, i, img.size[0], img.size[1]))
        tests.append((orig, new_img))

    sys.stdout.write('...')
    sys.stdout.flush()
    for entry in tests:
        loc = find_loc_double_check(*entry)
        if loc:
            print "\n", entry[1].info, "Found in", entry[0].info
            res = place_image(subimg, entry[1], entry[0], loc, highlight=True)
            res.show()
            return
            # break
            # raw_input("Press Enter to continue...")
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
    raise Exception("Not Found")

def run_me(run_time=None):

    if run_time:
        start_time = time.time()

    # inp_paths = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'Two Crop test.png')]

    inp_paths = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'Two Crop test.png'),
                 os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'Two Crop test2.png')]
    orig_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'Two Infrared test.png')
    out_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'UnCropResult.png')

    orig = Image.open(orig_path)

    for img_path in inp_paths:
        try:
            img = Image.open(img_path)
            main(img, orig)
        except Exception as e:
            img = Image.open(img_path)
            main(img.transpose(Image.FLIP_LEFT_RIGHT), orig.transpose(Image.FLIP_LEFT_RIGHT))

    # img = Image.open('Input/Two Crop test3.png')
    #
    # ret = main(img, ret)
    # ret.show()

    if run_time:
        print("\n--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':

    run_me()

    sys.exit(0)
