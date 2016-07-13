from __future__ import division
import math
from PIL import Image
from PIL.ExifTags import TAGS
import os
import traceback
import sys
import warnings

# consult link for more info
#http://photoseek.com/2013/compare-digital-camera-sensor-sizes-full-frame-35mm-aps-c-micro-four-thirds-1-inch-type/

# resource for info on exif tags
#http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html

# more info on this solution
#http://stackoverflow.com/questions/22634518/how-to-get-distance-of-object-from-iphone-camera-using-image-exif-meta-data

# research on field of view
#http://petapixel.com/2013/06/15/a-mathematical-look-at-focal-length-and-crop-factor/

# better table of sensor heights
#http://www.scantips.com/lights/fieldofview.html#top

debug = 0
test_factor = 1 # set to manually control the ratio of the case from which focal length is determined to the known test case

# some useful sensor height to crop factor relations
dict = {'1/3.2': (3.42, 7.6), '1/3.0': (3.6, 7.2), '1/2.6': (4.1, 6.3), '1/2.5' : (4.29, 6.0), '1/2.3': (4.55, 5.6), '1/1.8': (5.32, 4.8), '1/1.7': (5.64, 4.7), '2/3': (6.6, 3.9), '16mm': (7.49, 3.4), '1': (8.80, 2.7), '4/3': (13,2.0), 'Imax': (52.63, 0.49)} # some useful sensor height to crop factor relations
key = None

object_in_question = 0.115  # Real vertical height of object being examined in meters
pix_pct = 0.0               # precise portion of vertical pixel occupied by object

directory = os.path.dirname(os.path.realpath(__file__))
image = directory + '\\Input\\IMG_0943.jpg'

def get_object_px(path):
    im = Image.open(path)
    img_width, img_height = im.size

    box = (126, 132, 158, 133)  # (126, 132, 161, 200)
    region = im.crop(box)       # insert procedure to determine what number of vertical pixels that is the object
    obj_height_px = region.size[0]

    # region.show()

    print "img dimensions", img_width, "x", img_height, "px"
    return obj_height_px, img_height

def get_exif(path):
    ret = {}
    i = Image.open(path)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def find_distance_given_height_secondary(height_pct, height_of_sensor_mm, focal_len_mm):
    global object_in_question
    theta = math.atan((height_pct * height_of_sensor_mm) / focal_len_mm)  # if height of object is X pct of the pixels, then it must also be X pct of the sensor height in mm
    goal_distance = object_in_question / math.tan(theta)
    return goal_distance

def find_distance_given_height_primary(obj_heigth_px, focal_len):
    global object_in_question
    test_angle = math.atan(obj_heigth_px / focal_len)
    goal_dist = object_in_question / math.tan(test_angle)
    return goal_dist

def find_key(fnumber):
    pass
    # 35 mm eq.Focal Length = Actual Focal Length * Crop Factor
    #https://mayukhmukherjee.wordpress.com/tag/crop-factor/

def find_sensor_height(image_height):
    # useless so far

    dimensions = get_object_px(image)
    pix_pct = (dimensions[1] / dimensions[2])
    sensor_height = pix_pct / get_exif(image)['YResolution'][0]

    if get_exif(image)['ResolutionUnit'] is 2:
        sensor_height = sensor_height * 25.4

    return sensor_height

def calibrate_focal_len(set_distance_of_object, object_height_px):
    a = object_in_question      # height in meters
    d = set_distance_of_object  # in meters
    control_angle = math.atan(a / d)    # achieve theta for this controlled case

    focal_len_px = object_height_px / math.tan(control_angle)
    return focal_len_px

def print_tags(tags):
    print "tags;"
    for key, val in tags.iteritems():
        print key, ": ", val

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    if not debug:
        global test_factor
        global object_in_question
        global pixel_pct
        dimensions = get_object_px(image)
        pix_pct = dimensions[0] / dimensions[1]
        dist = None

        print ("attempting to determine focal len using known properties (best)...")
        try:
            pix_pct = (dimensions[0] / test_factor) / dimensions[1]
            print "pix pct", pix_pct

            focal_len = calibrate_focal_len(1, dimensions[0])
            print "focal len px", focal_len

            dist = find_distance_given_height_primary((dimensions[0] / test_factor), focal_len)
            # raise Exception

        except Exception as e:
            sys.stderr.write("Failed.\n")
            traceback.print_exc()

            print ("attempting to investigate EXIF tags for focal len and sensor size (second best, method 1)...")
            try:
                pix_pct = (dimensions[0] / test_factor) / dimensions[1]
                print "pix pct", pix_pct

                tags = get_exif(image)
                print_tags(tags)

                # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
                focal_len = int(tags['FocalLength'][0]) / int(tags['FocalLength'][1])
                print "focal len mm", focal_len

                dist = find_distance_given_height_secondary(pix_pct, dict['1/3.0'][0], focal_len)
                # raise Exception

            except Exception as e:
                sys.stderr.write("Failed.\n")
                traceback.print_exc()

                print ("attempting to investigate EXIF tags for focal len and sensor size (second best method 2)...")
                try:
                    pix_pct = (dimensions[0] / test_factor) / dimensions[1]
                    print "pix pct", pix_pct

                    tags = get_exif(image)
                    print "tags", tags

                    # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
                    focal_len = float(tags['FocalLength'][0]) / float(tags['FocalLength'][1])
                    print "focal len mm", focal_len

                    dist = (focal_len * (object_in_question * 1000) * dimensions[1]) / ((dimensions[0] / test_factor) * dict['1/3.0'][0]) / 1000

                except Exception as e:
                    sys.stderr.write("Failed.\n")
                    traceback.print_exc()

                    print ("attempting to discover subject distance in EXIF (worst case)...")
                    try:
                        dist = get_exif(image)['SubjectDistance']  # maybe useful, determined from center of focus in digital cameras
                    except Exception as e:
                        sys.stderr.write("Failed.")
                        traceback.print_exc()
                        print "solution attempts exhausted, retiring\n"
        print "dist", dist

    else:
        dimensions = get_object_px(image)
        pix_pct = dimensions[0] / dimensions[1]
        print "pix pct", pix_pct

        print key, find_key(get_exif(image)['FNumber'])