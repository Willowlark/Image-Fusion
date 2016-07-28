from PIL import Image
import os, sys

def autorotate(inpath, outpath):

    """ This function auto rotates a picture """
    image = Image.open(inpath)
    exif_store = image.info['exif']
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
            image = image.rotate(rotate_values[orientation], resample=Image.BICUBIC, expand=True)
            image.show()
            image.save(outpath, quality=100, exif=exif_store)
            return True
    return False

def rotate(inpath, outpath, degree):

    image = Image.open(inpath)
    exif_store = image.info['exif']
    exif = image._getexif()
    if exif is not None:
        image = image.rotate(degree, resample=Image.BICUBIC, expand=True)
        image.show()
        image.save(outpath, quality=100, exif=exif_store)
        return True
    return False

def main():
    imgs = ['IMG_0988.jpg', 'IMG_0989.jpg', 'IMG_0990.jpg', 'IMG_0991.jpg', 'IMG_0992.jpg']
    for img in imgs:
        infile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', img)
        outfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'temp.jpg')
        print autorotate(infile, outfile)

def main2():
    h, w = Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input', 'IMG_0992.jpg')).size
    print w, h
    im = Image.new('RGB', (h, w))
    im.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Output', 'One Fused Provided.jpg'), quality=100)

if __name__ == '__main__':

    main()
    sys.exit(0)