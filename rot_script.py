from PIL import Image
import os

def autorotate(inpath, outpath):

    """ This function auto rotates a picture """
    image = Image.open(inpath)
    exif = image._getexif()

    orientation_key = 274 # cf ExifTags
    if orientation_key in exif:
        orientation = exif[orientation_key]

        rotate_values = {
            3: 180,
            6: 270,
            8: 90
        }

        if orientation in rotate_values:
            new = image.rotate(rotate_values[orientation], resample=Image.BICUBIC, expand=True)
            new.show()
            new.save(outpath, quality=100)
            return True
    return False

def rotate(inpath, outpath, degree):

    image = Image.open(inpath)
    exif = image._getexif()
    if exif is not None:
        new = image.rotate(degree, resample=Image.BICUBIC, expand=True)
        new.show()
        new.save(outpath, quality=100)
        return True
    return False

if __name__ == '__main__':
    infile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'IMG_0992.jpg')
    outfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'IMG_0992.jpg')
    print rotate(infile, outfile, 270)
    # print autorotate(infile, outfile)