from PIL import Image
import sys

"""
This class contains method that are desirable to functional application of the procedure of object distance detection
Theses two methods can be applied to manually rotate an image, and most importantly preserve the EXIF tags, through specification or by nature of the image being examined.
Auto-rotate will examine the exif tags for all images that are not upright with respect to the sensor of the camera.
Rotate requires a parametrized number value for the angle the image must be rotated (of value 360 to -360)
"""

def autorotate(inpath, outpath=None):
    """
    autorotate corrects an image's orientation for processing by the image_merge, pixelProcess, distance_finder, and calibration

    """

    image = Image.open(inpath)
    exif_store = image.info['exif']
    exif = image._getexif()

    orientation_key = 274 # cf ExifTags

    if exif is not None:

        if orientation_key in exif:
            orientation = exif[orientation_key]

            rotate_values = {3: 180, 6: 270, 8: 90}

            if orientation in rotate_values:
                image = image.rotate(rotate_values[orientation], resample=Image.BICUBIC, expand=True)
                image.show()

                if outpath is not None:
                    image.save(outpath, quality=100, exif=exif_store)
                else:
                    image.save(inpath, quality=100, exif=exif_store)
            return True

    return False

def rotate(degree, inpath, outpath=None):
    """
    rotate corrects an image's orientation based on specified parameter degree

    """

    image = Image.open(inpath)
    exif_store = image.info['exif']
    exif = image._getexif()

    if exif is not None:
        image = image.rotate(degree, resample=Image.BICUBIC, expand=True)
        image.show()

        if outpath is not None:
            image.save(outpath, quality=100, exif=exif_store)
        else:
            image.save(inpath, quality=100, exif=exif_store)

        return True
    return False

def debug():
    """
    used only in testing

    """

    infile = "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_rot_test.jpg"
    outfile = "/Users/robertseedorf/PycharmProjects/Image-Fusion/Output/temp.jpg"
    print autorotate(infile, outfile)

def main(inpath, outpath=None, degree=None):
    """
    method for use outside of the realm of the individual script

    """

    if degree is not None:
        return rotate(degree, inpath, outpath)
    else:
        return autorotate(inpath, outpath)

if __name__ == '__main__':
    """
    run-me
    """

    infile = sys.argv[1]
    outfile = None
    degree = None

    if len(sys.argv) > 2:
        outfile = sys.argv[2]
        if len(sys.argv) > 3:
            degree = float(sys.argv[3])

    print main(infile, outfile, degree)

    sys.exit(0)