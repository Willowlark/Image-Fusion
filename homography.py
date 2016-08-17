import cv2, os, PIL, ntpath, ImageMerge, PixelProcess, images2gif, Console
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from pprint import pprint
from Tkinter import *
from gif_player import gifPlayer

class Homography():
    """
    This class encapsulates the ability to dimensionally justify the perspective of a sequence of images using homography
    Homography is the process of 'warping' one image's perspective to match that of another's based on the dimensions of a commonly shared object.
    By correcting the perspective of a collection of images based on a commonly found difference, a '3D' effect is created to improve the visualization of an image

    First the image merge is applied across a collection of 'base images' and 'test images' to find the common difference in each.
    Next the objects are used to correct the varied image perspectives using opencv's homography methods.
    The collections of frames are cropped slightly to reduces the effects of the warped perspective and labeled with a signature name
    Finally they are applied to a gif manufacturing pre-fab, images2gif.py, which creates a gif file to be displayed
    """

    def __init__(self, base_imgs, test_imgs,):
        """
        constructor for one Homography instance

        `base_imgs` images to be used in image merge process, without object being examined
        `test_imgs` images to be used in image merge process, with object being examined
        """
        self.base_imgs = base_imgs
        self.test_imgs = test_imgs

    def exe(self, gif_path, dest_index, save_first_frame=False):

        args_count = 0

        frames_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gif_test', 'frames')

        im_dst = cv2.imread(self.base_imgs[dest_index])

        pts_dst = np.array(self.obtain_dimensions(self.base_imgs[dest_index], self.test_imgs[dest_index]))

        h, status = cv2.findHomography(pts_dst, pts_dst)
        im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

        if save_first_frame is True:
            cv2.imwrite(os.path.join(frames_dir, 'frame' + str(args_count) + '.png'), im_out)

        # Note: the images of base and test are aligned for merging using their respective indices in parallel
        for index in xrange(0, len(self.base_imgs)):
            args_count += 1

            im_src = cv2.imread(self.test_imgs[index])

            pts_src = np.array(self.obtain_dimensions(self.base_imgs[index], self.test_imgs[index]))

            h, status = cv2.findHomography(pts_src, pts_dst)
            im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1], im_dst.shape[0]))

            cv2.imwrite(os.path.join(frames_dir, 'frame' + str(args_count) + '.png'), im_out)

        print 'file args processed', args_count

        self.trim_imgs(frames_dir, 0.15)
        apply_names(frames_dir)

        file_names = sorted(
            ('gif_test/frames/' + fn for fn in os.listdir(frames_dir) if
             fn.endswith('.png')))

        print 'frames:'
        pprint(file_names)

        images = self.modularize_frames(file_names, omit_first_and_last=True)

        images2gif.writeGif(gif_path, images, duration=0.4)

        return

    def trim_imgs(self, direc, pct_off):
        """
        Method to trim images of excess void

        `direc` direct of containing all files to be cropped
        `pct_off` the float value for pixels to be removed from each side of the image, im
        """
        for fn in os.listdir(direc):
            crop_by_size(os.path.join(direc, fn), pct_off)

    def modularize_frames(self, file_names, omit_first_and_last=True):
        """
        This method orders and returns the list of frames to be passed for gif manufacture.
        Goal: to order the images to produce realistic, 3D rotational perspective

        `file_names` list of file names to be ordered
        `omit_first_and_last` flag to denote the intentional removal of redundant fist and last frames
        `return` list of frames in order
        """
        lis_forw = [PIL.Image.open(fn) for fn in file_names]
        if omit_first_and_last:
            lis_remain = lis_forw[::-1][1:-1]
        else:
            lis_remain = lis_forw[::-1]
        return lis_forw + lis_remain

    def obtain_dimensions(self, base_file, obj_file):
        """
        Deployent of image merge to colelct relative width and height of object, differece, essential to perspective correction

        `base_file` image merge base image
        `obj_file` the test file of image merge
        `return` dimensions of box surrounding image difference (top left corner, top right corner, bottom left corner, bottom right corner)
        """

        consolas = Console.Console('Output/ImF.png')
        consolas.do_extractremote(None)
        consolas.do_redhighlight(None)
        consolas.do_colordiff(120)

        consolas.do_merge(base_file)
        consolas.do_merge(obj_file)

        consolas.do_gengroups(None)
        consolas.do_countsortgroups(None)
        f = consolas.groups.first()

        # corners of object from merge
        top_right = [f.x[0],f.y[0]]
        bottom_left = [f.x[1], f.y[1]]
        top_left = [f.x[1], f.y[0]]
        bottom_right = [f.x[0], f.y[1]]

        return top_left, top_right, bottom_right, bottom_left

def apply_names(direc):
    """
    Mehtod to apply names, in format of text_on_image to all files of specified directory, direc.

    `direc` directory of files to be 'labeled'
    """
    for fn in os.listdir(direc):
        if fn.endswith('.png'):
            text_on_image(os.path.join(direc, fn))

def clear_frames(direc):
    """
    Method to clear all files from a specified directory, direc
    WARNING, use with caution

    `direc` directory to be emptied
    """
    for f in os.listdir(direc):
        os.remove(os.path.join(direc, f))

def resize_by_image(destination, source):
    """
    Method to resize and image, destination, to fit the dimensions of another image, source

    `destination` image file to be re-sized
    `source` source of image whose dimensions will be used to resize, destination
    """
    resize_by_size(destination, *PIL.Image.open(source).size)

def resize_by_size(file, new_w, new_h):
    """
    Method to manually resize image by specified dimensions

    `file` image to be re-sized
    `new_w` new specified width of image
    `new_h` new specified height of image
    """
    img = PIL.Image.open(file)
    img = img.resize((new_w, new_h), PIL.Image.ANTIALIAS)
    img.save(file)

def crop_by_size(file, edge_pct):
    """
    Method to crop specified percent of pixels form each side

    `file` image file to be cropped
    `edge_pct` percent of pixels to be removed
    """
    img = PIL.Image.open(file)
    w, h = img.size
    half_pct = edge_pct / 2
    img = img.crop((int(half_pct*w), int(half_pct*h), w-int(half_pct*w), h-int(half_pct*h)))
    img.save(file)

def text_on_image(path):
    """
    Using ImageDraw, the image can be labeled with a name in the picture

    `path` image to be labeled
    """
    img = PIL.Image.open(path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 15)
    draw.text((0, 0), ntpath.basename(path), (255, 255, 255), font=font)
    img.save(path)

def debug_main():
    """
    Debug exe file for testing
    TODO remove after testing
    """

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    frames_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gif_test', 'frames')
    inp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input')

    # apply_image_merge(os.path.join(inp_dir, 'IMG_0991.jpg'), os.path.join(inp_dir, 'IMG_0993.jpg'))

    im_dst = cv2.imread('Input/IMG_0993.png')
    pts_dst = np.array([[179, 196], [179, 205], [198, 196], [198, 205]])
    h, status = cv2.findHomography(pts_dst, pts_dst)
    im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

    if len(sys.argv) > 1 and sys.argv[1] is not '0':
        cv2.imwrite(os.path.join(frames_dir, 'frame0.png'), im_out)

    im_src1 = cv2.imread('Input/IMG_1004.png')
    pts_src1 = np.array([[1623, 1149], [1623, 1405], [2282, 1149], [2282, 1405]])
    h, status = cv2.findHomography(pts_src1, pts_dst)
    im_out = cv2.warpPerspective(im_src1, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame1.png'), im_out)

    im_src2 = cv2.imread('Input/IMG_0991.png')
    pts_src2 = np.array([[116, 155], [116, 125], [179, 155], [179, 125]])
    h, status = cv2.findHomography(pts_src2, pts_dst)
    im_out = cv2.warpPerspective(im_src2, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame2.png'), im_out)

    apply_names(frames_dir)

    file_names = sorted(
        (os.path.join('gif_test', 'frames', fn) for fn in os.listdir(frames_dir) if fn.endswith('.png')))
    pprint(file_names)

    images = [PIL.Image.open(fn) for fn in file_names]

    gif_file = os.path.join(os.path.dirname(os.path.realpath(frames_dir)), 'my_gif.GIF')
    images2gif.writeGif(gif_file, images, duration=0.5)

    return

if __name__ == '__main__' :
    """
    Script run-me execution to complete functionality

    """

    # applicable run-me
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    frames_dir = os.path.join(cur_dir, 'gif_test', 'frames')
    inp_dir = os.path.join(cur_dir, 'Input')

    gif_path = os.path.join(cur_dir, 'gif_test', 'res_gif.GIF')

    bases = [os.path.join(inp_dir, 'IMG_1022.jpg'), os.path.join(inp_dir, 'IMG_1024.jpg'), os.path.join(inp_dir, 'IMG_1026.jpg')]
    tests = [os.path.join(inp_dir, 'IMG_1021.jpg'), os.path.join(inp_dir, 'IMG_1023.jpg'), os.path.join(inp_dir, 'IMG_1025.jpg')]
    dest = (os.path.join(inp_dir, 'IMG_1024.jpg'), os.path.join(inp_dir, 'IMG_1023.jpg'))

    clear_frames(frames_dir)

    hg = Homography(base_imgs=bases, test_imgs=tests)
    hg.exe(gif_path, dest_index=1, save_first_frame=False)

    root = Tk()
    anim = gifPlayer(root, gif_path)
    anim.pack()
    anim.run(root)