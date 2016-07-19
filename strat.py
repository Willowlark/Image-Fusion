from __future__ import division
import math
from PIL import Image
from PIL.ExifTags import TAGS
import os
import traceback
import sys
import warnings

# run me
warnings.filterwarnings('ignore')

debug = 0
test_factor = 0.10 # set to manually control the ratio of the case from which focal length is determined to the known test case

# some useful sensor height to crop factor relations
dict = {'1/3.2': (3.42, 7.6), '1/3.0': (3.6, 7.2), '1/2.6': (4.1, 6.3), '1/2.5' : (4.29, 6.0), '1/2.3': (4.55, 5.6), '1/1.8': (5.32, 4.8), '1/1.7': (5.64, 4.7), '2/3': (6.6, 3.9), '16mm': (7.49, 3.4), '1': (8.80, 2.7), '4/3': (13,2.0), 'Imax': (52.63, 0.49)} # some useful sensor height to crop factor relations
key = None

object_in_question = 0.115  # Real vertical height of object being examined in meters

directory = os.path.dirname(os.path.realpath(__file__))
image = directory + '/Input/IMG_0942.jpg'

def get_object_px(path):
    """
    This method should will be finished to find the height of the found object in pixels
    to be used essential to every distance method

    `path` the path to the image file being investigated
    `return` (obj_height, img_height) the height of teh object in px, and the height of the image in pixels
    """
    im = Image.open(path)
    img_width, img_height = im.size

    # TODO insert procedure to determine what number of vertical pixels that is the object
    # these values were calculated by hand and visual estimation, they wil be done with a sub-procedure upon completion
    box = (126, 132, 158, 133)  # (126, 132, 161, 200)
    region = im.crop(box)
    obj_height_px = region.size[0]

    # region.show()

    print "img dimensions", img_width, "x", img_height, "px"
    return obj_height_px, img_height

def get_exif(path):
    """
    Method to return the exif tags of the file at path

    `path` the path to local file that is opened and parsed for exif tags
    `return` ret, the dictionary of all tags and their values
    """
    ret = {}
    i = Image.open(path)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def find_distance_given_height_secondary(height_pct, sensor_height_mm, focal_len_mm):
    """
    This method takes the percent of the image's vertical pixels that are occupied by object being examined, the known height of the sensor in mm, and the known focal length to determine the distance of the object from the aperture

    `height_pct' height of object as floating value in vertical pixels occupied
    `sensor_height_mm` the known height of the sensor in millimeters
    `focal_len_mm the known focal len of the sensor in millimeters
    `return` the determined distance of the object from the camera in units of object_in_question
    """
    global object_in_question
    theta = math.atan((height_pct * sensor_height_mm) / focal_len_mm)  # if height of object is X pct of the pixels, then it must also be X pct of the sensor height in mm
    goal_dist = object_in_question / math.tan(theta)
    return goal_dist

def find_distance_given_height_primary(obj_height_px, focal_len_px):
    """
    This method takes the height of the object in pixels and the determined focal_length in pixels to find the distance to that object

    `obj_height_px` the height of the object in pixels
    `return` the determined distance of the object from the camera in units of object_in_question
    """
    global object_in_question
    test_angle = math.atan(obj_height_px / focal_len_px)
    goal_dist = object_in_question / math.tan(test_angle)
    return goal_dist

def find_key(eq_focal_len, act_focal_len):
    """
    This method determinethe key to beused to access the dictionary, dict, of the commonly used camera sizes and their info
    :param eq_focal_len:
    :param act_focal_len:
    :return:
    """
    global key
    crop_fact = eq_focal_len / act_focal_len
    for k, v in dict.iteritems():
        if v[1] + 0.3 >  crop_fact and v[1] - 0.3 <  crop_fact: # If calculated crop factor is with +- 0.3 units of the known than it is accepted
            key = k
            break

def find_sensor_height(image_height):
    # useless so far
    # maybe used to find sensor height in mm
    dimensions = get_object_px(image)
    pix_pct = (dimensions[1] / dimensions[2])
    sensor_height = pix_pct / get_exif(image)['YResolution'][0]

    if get_exif(image)['ResolutionUnit'] is 2:
        sensor_height = sensor_height * 25.4

    return sensor_height

def calibrate_focal_len(control_object_distance, control_object_height_px):
    """
    this method will find the necessary value for focal length using the founding principles of similar angles applied using trigonometry
    When the known distance of the object, and the fixed, known height of the object are used to calibrate for the arbitrary angle, control angle
    they can be used to find the focal length, assuming the same percent of the sensor is occupied by the object as is occupied in the photograph

    `control_object_distance` the fixed, measured distance used for calibration
    `control_object_height_px` the fixed, measured height in pixels of teh object's visage in the digital photo
    `return` focal length in pixels
    """
    a = object_in_question      # height in meters
    d = control_object_distance  # in meters

    control_angle = math.atan(a / d)    # achieve theta for this controlled case
    focal_len_px = control_object_height_px / math.tan(control_angle)
    return focal_len_px

def print_tags(tags):
    print "tags;"
    for key, val in tags.iteritems():
        print key, ": ", val

class Solution:
    def execute(self): pass

class Primary(Solution):
    def execute(self):
        try:
            pix_pct = (dimensions[0] * test_factor) / dimensions[1]
            # print "pix pct", pix_pct

            focal_len = calibrate_focal_len(1, dimensions[0])
            # print "focal len px", focal_len

            dist = find_distance_given_height_primary((dimensions[0] * test_factor), focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Primary Method Failed.\n")
            traceback.print_exc()

class Secondary(Solution):
    def execute(self):
        try:
            pix_pct = (dimensions[0] * test_factor) / dimensions[1]
            # print "pix pct", pix_pct

            tags = get_exif(image)
            # print_tags(tags)

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            focal_len = int(tags['FocalLength'][0]) / int(tags['FocalLength'][1])
            # print "focal len mm", focal_len

            find_key(tags['FocalLengthIn35mmFilm'], float(tags['FocalLength'][0]) / float(tags['FocalLength'][1]))
            # print "determined key", key + "\""

            dist = find_distance_given_height_secondary(pix_pct, dict[key][0], focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Secondary Method Failed.\n")
            traceback.print_exc()

class Tertiary(Solution):
    def execute(self):
        try:
            tags = get_exif(image)
            #print "tags", tags

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            focal_len = float(tags['FocalLength'][0]) / float(tags['FocalLength'][1])
            #print "focal len mm", focal_len

            find_key(tags['FocalLengthIn35mmFilm'], float(tags['FocalLength'][0]) / float(tags['FocalLength'][1]))
            #print "determined key", key + "\""

            dist = (focal_len * object_in_question * dimensions[1]) / (
            (dimensions[0] * test_factor) * dict[key][0])
            return dist

        except Exception as e:
            sys.stderr.write("Tertiary Method Failed.\n")
            traceback.print_exc()

class Quaternary(Solution):
    def execute(self):
        try:
            dist = get_exif(image)['SubjectDistance']  # maybe useful, determined from center of focus in digital cameras
            return dist
        except Exception as e:
            sys.stderr.write("Quaternary Method Failed.")
            traceback.print_exc()

# An object that holds commands:
class Macro:
    def __init__(self):
        self.commands = []
    def add(self, command):
        self.commands.append(command)
    def run(self):
        for c in self.commands:
            print "DIST", repr(c), c.execute()

dimensions = get_object_px(image)
pix_pct = dimensions[0] / dimensions[1]

# run me
macro = Macro()
macro.add(Primary())
macro.add(Secondary())
macro.add(Tertiary())
# macro.add(Quaternary())
macro.run()