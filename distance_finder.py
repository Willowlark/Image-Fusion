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
from pixel_height_finder import pixel_height_finder

# EXAMPLE ARGS
# 0.115 IMG_0942.jpg

class Solution:
    """
    This class represents one solution given a single case of image distance finding.
    Given the parametrized vargs, index 1: image to be examined, and index 2: the known height in meters of highlighted object,
    The solution's constructor and find distance command will return the distance of the object highlighted in the image
    Four variations of this task exist, The primary, Secondary, Tertiary, and Quaternary.
    Each works based on the capability of the pre-conditioned machine (Primary), or as fail-safe, the exif tags of the test image (Secondary, Tertiary, and Quaternary).
    The Primary reads in from the calib_info file, the calibrated info used to find the focal length and the focal length determined,
    then using trigonometric principals of similar angles, the distance of the object, whose height is known, is found.
    The Secondary, and Tertiary methods use the exif tags to find the focal length of the lens in the camera that was used, and apply that focal length to the trigonometry.
    The final method, investigates the tags for a special 'subject distance' tag that assumes the accurate region of focus and returns that distance fom the camera
    """

    def __init__(self, infile, known_height):
        self.test_factor = 0.01 # TODO remove this when done
        self.test_image = infile
        self.height_object_in_question = known_height
        self.key = None
        self.focal_len = None

        directory = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(directory, 'json', 'cameras.json'), 'r') as data_file:
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

        red = (249, 24, 0)
        phf = pixel_height_finder(red)

        # TODO it is here the procedure of image merging belongs, This is temp solution to make visible the intentional difference
        out = phf.pixel_write(path).rotate(-90)
        out.show()

        res = phf.find_height(out)
        print "obj height px", res[0], "\nvert px pct", res[1]
        return (res[0] * self.test_factor, img_height)

        # these values were calculated by hand and visual estimation, they wil be done with a sub-procedure upon completion
        # box = (126, 132, 158, 133)  # (126, 132, 161, 200)
        # region = im.crop(box)
        # obj_height_px = region.size[0]
        #
        # region.show()
        # print "img dimensions", img_width, "x", img_height, "px"
        #
        # return obj_height_px * self.test_factor, img_height

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
        """
        inherited method to be used by each subclass in a particular way
        :return: distance, in meters of object from aperture, if solution available, else None
        """
        pass

class Primary(Solution):
    """
    The described primary method of finding object distance
    Requires config file (calib_info) to be established for accurate functionality
    """

    def __init__(self, infile, known_height):
        Solution.__init__(self, infile, known_height)

        with open(os.path.join(directory, 'json', 'calib_info.json'), 'r') as fp:
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

            dist = self.find_distance_given_height_primary(dimensions[0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Primary Method Failed.\n")
            traceback.print_exc()

class Secondary(Solution):
    """
    The described secondary method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """
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

            dist = self.find_distance_given_height_primary(pix_pct * self.camera_dict[key][0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Secondary Method Failed.\n")
            traceback.print_exc()

class Tertiary(Solution):
    """
    The penultimate method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """

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
    """
    The last method of finding object distance, characterized by unreliability
    Requires proper file format, with exif tags, as well as exif tag 'SubjectDistance' and assumes the object is in field of focus
    """

    def __init__(self, infile, known_height):
        Solution.__init__(self, infile, known_height)
    
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
            ret.append((str(c.__class__.__name__), os.path.split(c.test_image)[1], c.find_distance()))
        return ret

def main(infile, known_height):

    # run me
    df = Macro(Primary(infile, known_height), Secondary(infile, known_height), Tertiary(infile, known_height))
    results = df.run()
    pprint(results)

if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    directory = os.path.dirname(os.path.realpath(__file__))
    infile = os.path.join(directory, 'Input', str(sys.argv[2]))
    #main(infile, 1.82 * 0.85)
    main(infile, float(sys.argv[1]))    # argv[1]: 1.82 (in meters)
    #main(infile, 1.82 * 1.15)

    sys.exit(0)