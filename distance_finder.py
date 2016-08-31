from __future__ import division
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import math, os, traceback, sys, warnings, json, Console, subprocess, ntpath

"""
EXAMPLE ARGS
1.82 "P,S,T" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_base.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_two.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_onehalf.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_half.jpg"

1.82 = the actual height of the object whose distance is being sought, in meters
"P,S,T" = the argument list of the methods chosen to be applied during the distance solving process, as denoted by the first letter of the name. comma delimited list
"first/file/path" = the base file, against which all subsequent files are compared for difference extraction and examination
"all/subsequent/files/path" = the files wherein the difference to be examined lies

INDEPENDENT CALL EXAMPLE:
procedure = Primary(base.jpg, input.jpg, 1.82)
procedure.find_distance()
"""


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

    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for one solution object.

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """
        self.base_file = base_file
        self.obj_file = obj_file
        self.height_object_in_question = known_height
        self.focal_len = None

        directory = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(directory, 'json', 'cameras.json'), 'r') as data_file:
            data = json.load(data_file)
            self.camera_dict = data

    def config(self, base_file, obj_file, known_height):
        self.base_file = base_file
        self.obj_file = obj_file
        self.height_object_in_question = known_height
        return self

    def get_object_height_px(self, base_file, obj_file):
        """
        This method should will be finished to find the height of the found object in pixels
        to be used essential to every distance method

        `path` the path to the image file being investigated
        `return` (obj_height, img_height) the height of the object in px, and the height of the image in pixels
        """
        im = Image.open(obj_file)
        img_width, img_height = im.size

        consolas = Console.Console('Output/ImF.png')
        consolas.do_extractremote(None)
        consolas.do_redhighlight(None)
        consolas.do_colordiff(120)

        consolas.do_merge(base_file)
        consolas.do_merge(obj_file)

        consolas.do_gengroups(None)
        consolas.do_countsortgroups(None)
        first = consolas.groups.first()

        # print "object @", first
        # ratio = first.height / Image.open(base_file).height
        # print Image.open(base_file).height
        # print "pct of height", ratio
        #
        #
        # print "obj height px", first.height, "\nimage height px", img_height

        return first.height, img_height, first.x, first.y

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

    def find_key(self, eq_focal_len, act_focal_len):
        """
        This method determines the key to be used to access the dictionary, camera_dict, of the commonly used camera sizes and their info
        Using the 35 mm equivalent focal length (read in through EXIF tags) and the actual focal length (also read in through EXIF tags) are used to find the crop factor where...

        crop factor = 35mm eq / actual focal length

        NOTE, the accuracy of the sensor height being yielded are dependent on the secondary value, crop factor
        crop factor will fall with +- 0.3 units of the desired key to yield the result

        :param eq_focal_len: 35 mm equivalent focal length
        :param act_focal_len: actual focal length in mm
        :return: the key to be used for later dictionary indexing
        """
        global key
        crop_fact = eq_focal_len / act_focal_len
        for k, v in self.camera_dict.iteritems():
            if v[1] + 0.3 > crop_fact and v[
                1] - 0.3 < crop_fact:  # If calculated crop factor is within +- 0.3 units of the known, then it is accepted
                return str(k)

    def find_distance(self):
        """
        inherited method to be used by each subclass in a particular way
        `return` distance, in meters of object from aperture, if solution available, else None
        """
        pass

class Primary(Solution):
    """
    The described primary method of finding object distance
    Requires config file (calib_info) to be established for accurate functionality
    """

    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for Primary method of execution.

        Note the extraction of info from the calibration json, calib_info, is  performed here. Should this procedure fail, the error will be printer but the object still constructed
        It will exist but it will not be functional, unless the calibration is successfully executed in the __init__

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """

        Solution.__init__(self, base_file, obj_file, known_height)
        with open(os.path.join(directory, 'json', 'calib_info.json'), 'r') as fp:
            json_data = json.load(fp)
            try:
                self.focal_len = json_data["focal_len"]
            except KeyError as ke:
                sys.stderr.write("WARNING no focal length found, primary method will fail.\n")
                sys.stderr.write(str(ke))
    
    def find_distance(self):
        """
        This method executes the tasks in order to find the distance of the object of the merge highlight
        The differentiating factor that delineates this method from Secondary and Tertiary is the use of calibrated focal length

        Using the math library, the arctangent of the height of the object in pixels divided byt he determined focal_length to find the angle of refraction, of the light through the lens.
        This angle is used with the known height of the object to find distance using the property of tangent(angle) = opposite / adjacent
        """
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)

            test_angle = math.atan(dimensions[0] / self.focal_len)
            dist = float(self.height_object_in_question) / math.tan(test_angle)

            return dist, dimensions[2], dimensions[3]

        except Exception as e:
            sys.stderr.write("Primary Method Failed.\n")
            traceback.print_exc()

class Secondary(Solution):
    """
    The described secondary method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """
    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for Secondary method of execution.

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        """
        This method executes the tasks in order to find the distance of the object of the merge highlight

        Using the math library, the arctangent of the height of the object in pixels divided byt he determined focal_length to find the angle of refraction, of the light through the lens.
        This angle is used with the known height of the object to find distance using the property of tangent(angle) = opposite / adjacent
        """
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            pix_pct = dimensions[0] / dimensions[1]
            tags = self.get_exif(self.obj_file)

            self.focal_len = int(tags['FocalLength'][0]) / int(tags['FocalLength'][1])

            key = self.find_key(tags['FocalLengthIn35mmFilm'], int(tags['FocalLength'][0]) / int(tags['FocalLength'][1]))

            test_angle = math.atan(pix_pct * self.camera_dict[key][0] / self.focal_len)
            dist = float(self.height_object_in_question) / math.tan(test_angle)

            return dist, dimensions[2], dimensions[3]

        except Exception as e:
            sys.stderr.write("Secondary Method Failed.\n")
            traceback.print_exc()

class Tertiary(Solution):
    """
    The penultimate method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """
    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for Tertiary method of execution.

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        """
        This method executes the tasks in order to find the distance of the object of the merge highlight

        Using the math library, the arctangent of the height of the object in pixels divided byt he determined focal_length to find the angle of refraction, of the light through the lens.
        This angle is used with the known height of the object to find distance using the property of tangent(angle) = opposite / adjacent
        """
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            tags = self.get_exif(self.obj_file)
            self.focal_len = float(tags['FocalLength'][0]) / float(tags['FocalLength'][1])

            key = self.find_key(tags['FocalLengthIn35mmFilm'], int(tags['FocalLength'][0]) / int(tags['FocalLength'][1]))

            dist = (self.focal_len * self.height_object_in_question * dimensions[1]) / (
                dimensions[0] * self.camera_dict[key][0])
            return dist, dimensions[2], dimensions[3]

        except Exception as e:
            sys.stderr.write("Tertiary Method Failed.\n")
            traceback.print_exc()

class Quaternary(Solution):
    """
    The last method of finding object distance, characterized by unreliability
    Requires proper file format, with exif tags, as well as exif tag 'SubjectDistance' and assumes the object is in field of focus
    """
    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for Quaternary method of execution.

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        """
        This method investigates the exif tags to find the SubjectDistance tag that may reveal the concerning information

        """
        try:
            dist = self.get_exif(self.obj_file)['SubjectDistance']  # maybe useful, determined from center of focus in digital cameras
            return dist

        except Exception as e:
            sys.stderr.write("Quaternary Method Failed.")
            traceback.print_exc()

class Macro:
    """
    This class holds the capability of running several 'commands,' as instances of subclasses, to be readily used in extension
    Stores list of 'methods' using strategy pattern. the commands list holds object of the Solution class tha implement a find_distance method
    """
    def __init__(self, *args):
        self.commands = []
        for arg in args:
            self.commands.append(arg)

    def add(self, command):
        self.commands.append(command)

    def run(self):
        ret = []
        for c in self.commands:
            ret.append((str(c.__class__.__name__), os.path.split(c.obj_file)[1], c.find_distance()))
        return ret

def text_on_image(image, text, location=(0, 0), color=(255,255,255)):
    """
    Using ImageDraw, the image can be labeled with a name in the picture

    `path` image to be labeled
    """
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text(location, text, color, font=font)
    return img

def main(known_height, method_flags, base_file, infiles):
    """
    run me method for scripting usage
    for deployment usage see additional example args at file head

    most useful individual deployment example (see line 325-328)
    df = Macro(Primary(infile, known_height), Secondary(infile, known_height), Tertiary(infile, known_height))

    `known_height` the known height in meters of the object in the picture
    `method_flags` the list of flags chosen to denote the choice of method used to solve (P - primary,S -secondary, etc.)
    `base_file` the base file against which all infiles will be checked and distance solved
    `infiles` the lis tof file being examined for difference, and determining distance
    `return` the list of results of upon execution
    """

    flags_list = method_flags.split(",")

    configs = {'P':Primary, 'S':Secondary, 'T':Tertiary, 'Q':Quaternary}

    df = Macro()
    for flag in flags_list:
        for obj_file in infiles:
            df.add(configs[flag.upper()](known_height=known_height, obj_file=obj_file, base_file=base_file))

    results = df.run()
    return results

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    directory = os.path.dirname(os.path.realpath(__file__))

    infiles = sys.argv[4:]                                                                                              # argv[4:] = all of the files for the script to be run over
    results = main(known_height=float(sys.argv[1]), method_flags=sys.argv[2], base_file=sys.argv[3], infiles=infiles)       # argv[1] =  0.124, height of object in meters, argv[3] = base image file pathname (absolute)

    # res is the collection of results of each call ordered first by the method(s) chosen, then by the input files.
    pprint(results)

    slideshow =[]
    for res in results[0:3]:
        image, text, location = os.path.join("Input", res[1]), str(res[2][0]), res[2][1]
        im = text_on_image(image, text, location, color=(255,0,0))
        im.save(os.path.join(directory, "slideshow", ntpath.basename(image)))
        slideshow.append(os.path.join(directory, "slideshow", ntpath.basename(image)))

    for file in slideshow:
        p = subprocess.Popen(["mspaint.exe", file])
        p.wait()

    sys.exit(0)