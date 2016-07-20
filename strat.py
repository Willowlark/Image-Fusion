from __future__ import division
from pprint import pprint
import math
from PIL import Image
from PIL.ExifTags import TAGS
import os
import traceback
import sys
import warnings
import json


class Solution:

    def __init__(self, infile, known_height):
        self.test_factor = 0.1  # TODO remove this when done
        self.test_image = infile
        self.height_object_in_question = known_height
        self.key = None
        self.focal_len = None

        directory = os.path.dirname(os.path.realpath(__file__))

        with open(directory + '\\json\\cameras.json', 'r') as data_file:
            data = json.load(data_file)
            self.camera_dict = data

    def get_object_px(self, path):
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
        # print "img dimensions", img_width, "x", img_height, "px"

        return obj_height_px * self.test_factor, img_height

    def get_exif(self, path):
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

    def find_distance_given_height_secondary(self, height_pct, sensor_height_mm, focal_len_mm):
        """
        This method takes the percent of the image's vertical pixels that are occupied by object being examined, the known height of the sensor in mm, and the known focal length to determine the distance of the object from the aperture

        `height_pct' height of object as floating value in vertical pixels occupied
        `sensor_height_mm` the known height of the sensor in millimeters
        `focal_len_mm the known focal len of the sensor in millimeters
        `return` the determined distance of the object from the camera in units of height_object_in_question
        """
        theta = math.atan((height_pct * sensor_height_mm) / focal_len_mm)  # if height of object is X pct of the pixels, then it must also be X pct of the sensor height in mm
        goal_dist = float(self.height_object_in_question) / math.tan(theta)
        return goal_dist

    def find_distance_given_height_primary(self, obj_height_px, focal_len_px):
        """
        This method takes the height of the object in pixels and the determined focal_length in pixels to find the distance to that object

        `obj_height_px` the height of the object in pixels
        `return` the determined distance of the object from the camera in units of height_object_in_question
        """
        test_angle = math.atan(obj_height_px / focal_len_px)
        goal_dist = float(self.height_object_in_question) / math.tan(test_angle)
        return goal_dist

    def find_key(self, eq_focal_len, act_focal_len):
        """
        This method determinethe key to beused to access the dictionary, dict, of the commonly used camera sizes and their info
        :param eq_focal_len:
        :param act_focal_len:
        :return:
        """
        global key
        crop_fact = eq_focal_len / act_focal_len
        for k, v in self.camera_dict.iteritems():
            if v[1] + 0.3 > crop_fact and v[
                1] - 0.3 < crop_fact:  # If calculated crop factor is with +- 0.3 units of the known than it is accepted
                key = k
                break

    def calibrate_focal_len(self, control_object_distance, control_object_height_px):
        """
        this method will find the necessary value for focal length using the founding principles of similar angles applied using trigonometry
        When the known distance of the object, and the fixed, known height of the object are used to calibrate for the arbitrary angle, control angle
        they can be used to find the focal length, assuming the same percent of the sensor is occupied by the object as is occupied in the photograph

        `control_object_distance` the fixed, measured distance used for calibration
        `control_object_height_px` the fixed, measured height in pixels of teh object's visage in the digital photo
        `return` focal length in pixels
        """
        control_angle = math.atan(self.height_object_in_question / control_object_distance)  # achieve theta for this controlled case
        focal_len_px = control_object_height_px / math.tan(control_angle)
        return focal_len_px

    def find_distance(self):
        pass

class Primary(Solution):

    def __init__(self, infile, known_height):
        Solution.__init__(self, infile, known_height)

        with open(directory + '\\json\\calib_info.json', 'r') as fp:
            json_data = json.load(fp)
            try:
                self.focal_len = json_data["focal_len"]
            except KeyError as ke:
                sys.stderr.write("WARNING no focal length found, primary method will fail.\n")
                sys.stderr.write(str(ke))
    
    def find_distance(self):
        try:
            dimensions = self.get_object_px(self.test_image)
            pix_pct = dimensions[0] / dimensions[1]
            # print "pix pct", pix_pct

            # focal_len = self.calibrate_focal_len(self.dist_object_in_question, self.get_object_px(self.calibration_image)[0])
            # # print "focal len px", focal_len

            dist = self.find_distance_given_height_primary(dimensions[0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Primary Method Failed.\n")
            traceback.print_exc()

class Secondary(Solution):

    def __init__(self, infile, known_height):
        Solution.__init__(self, infile, known_height)
    
    def find_distance(self):
        try:
            dimensions = self.get_object_px(self.test_image)
            pix_pct = dimensions[0] / dimensions[1]
            # print "pix pct", pix_pct

            tags = self.get_exif(self.test_image)
            # pprint(tags)

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            self.focal_len = int(tags['FocalLength'][0]) / int(tags['FocalLength'][1])
            # print "focal len mm", focal_len

            self.find_key(tags['FocalLengthIn35mmFilm'], float(tags['FocalLength'][0]) / float(tags['FocalLength'][1]))
            # print "determined key", key + "\""

            dist = self.find_distance_given_height_secondary(pix_pct, self.camera_dict[key][0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Secondary Method Failed.\n")
            traceback.print_exc()

class Tertiary(Solution):

    def __init__(self, infile, known_height):
        Solution.__init__(self, infile, known_height)
    
    def find_distance(self):
        try:
            dimensions = self.get_object_px(self.test_image)
            pix_pct = dimensions[0] / dimensions[1]
            # print "pix pct", pix_pct

            tags = self.get_exif(self.test_image)
            # pprint(tags)

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            self.focal_len = float(tags['FocalLength'][0]) / float(tags['FocalLength'][1])
            #print "focal len mm", focal_len

            self.find_key(tags['FocalLengthIn35mmFilm'], float(tags['FocalLength'][0]) / float(tags['FocalLength'][1]))
            #print "determined key", key + "\""

            dist = (self.focal_len * self.height_object_in_question * dimensions[1]) / (
                dimensions[0] * self.camera_dict[key][0])
            return dist

        except Exception as e:
            sys.stderr.write("Tertiary Method Failed.\n")
            traceback.print_exc()

class Quaternary(Solution):

    def __init__(self, infile):
        Solution.__init__(self, infile)
    
    def find_distance(self):
        try:
            dist = self.get_exif(self.test_image)['SubjectDistance']  # maybe useful, determined from center of focus in digital cameras
            return dist
        except Exception as e:
            sys.stderr.write("Quaternary Method Failed.")
            traceback.print_exc()

# An object that holds commands:
class Macro:
    def __init__(self, *args):
        self.commands = []
        for arg in args:
            self.commands.append(arg)

    def add(self, command):
        self.commands.append(command)

    def run(self):
        ret = []
        for c in self.commands:
            ret.append((repr(c), c.find_distance()))
        return ret

def main(infile, known_height):

    # run me
    df = Macro(Primary(infile, known_height), Secondary(infile, known_height), Tertiary(infile, known_height))
    results = df.run()
    pprint(results)

if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    directory = os.path.dirname(os.path.realpath(__file__))
    infile = directory + '\\Input\\IMG_0943.jpg'
    main(infile, 1.82 * 0.85)
    main(infile, 1.82)
    main(infile, 1.82 * 1.15)

    sys.exit(0)