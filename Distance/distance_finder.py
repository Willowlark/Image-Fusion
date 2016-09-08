from __future__ import division
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import math, os, traceback, sys, warnings, json, Console, subprocess, argparse, itertools, cv2
from os import listdir
from os.path import isfile, join

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

"""
EXAMPLE ARGS:
--known_height_m 1.82 --methods P S T --base "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_base.jpg" --files "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_two.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_onehalf.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_half.jpg"

--known_height_m    = the actual height of the object whose distance is being sought, in meters
--methods           = the argument list of the methods chosen to be applied during the distance solving process, as denoted by the first letter of the name. comma delimited list
--base              = the base file, against which all subsequent files are compared for difference extraction and examination
--files             = the file(s) wherein the difference to be examined lies, must be at least one

ANOTHER COMMAND LINE EXAMPLE:
--known_height_m 0.124 --methods L --base "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_base.jpg" --files "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_two.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_half.jpg"

INDEPENDENT CALL EXAMPLE:
procedure = Primary(base_file=base.jpg, obj_file=input.jpg, known_height=1.82)
procedure.find_distance()
"""

directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

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

        with open(os.path.join(directory, 'json', 'cameras.json'), 'r') as data_file:
            data = json.load(data_file)
            self.camera_dict = data

    def config(self, base_file, obj_file, known_height):
        """
        Method used for latent assignment of crucial fields, before running investigative process

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        `return` the instance of class 'self' that now holds states for aforementioned fields
        """
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

        # the following are console commands to employ image merge
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

        `return` dist - the discovered distance that is the result of the procedure
                dimension[2] - the location of x coordinates that are the far left and right most pixels of difference
                dimension[3] - the location of y coordinates that are the far left and right most pixels of difference
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

        `return` dist - the discovered distance that is the result of the procedure
                dimension[2] - the location of x coordinates that are the far left and right most pixels of difference
                dimension[3] - the location of y coordinates that are the far left and right most pixels of difference
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

        `return` dist - the discovered distance that is the result of the procedure
                dimension[2] - the location of x coordinates that are the far left and right most pixels of difference
                dimension[3] - the location of y coordinates that are the far left and right most pixels of difference
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

        `return` dist - the discovered distance that is the result of the procedure
                dimension[2] - the location of x coordinates that are the far left and right most pixels of difference
                dimension[3] - the location of y coordinates that are the far left and right most pixels of difference
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
            return dist, None, None

        except Exception as e:
            sys.stderr.write("Quaternary Method Failed.")
            traceback.print_exc()

class Linear(Solution):
    """
    The control method of finding object distance
    Requires that subject whose distance is being determined be the object of calibration process.
    and pixel height of image in subject file and control height variable (heigh_object_in_question)
    """
    def __init__(self, base_file=None, obj_file=None, known_height=None):
        """
        constructor for Linear method of execution.

        `base_file` the base file against which the obj_file will be checked and distance solved
        `obj_file` the file being examined for difference, and determining distance
        `known_height` the known height in meters of the object in the picture
        """
        Solution.__init__(self, base_file, obj_file, known_height)
        with open(os.path.join(directory, 'json', 'calib_info.json'), 'r') as fp:
            json_data = json.load(fp)
            try:
                self.known_height_px = json_data["control_object_height_px"]
            except KeyError as ke:
                sys.stderr.write("WARNING no control height in px found, method will fail.\n")
                sys.stderr.write(str(ke))
            try:
                self.known_dist = json_data["dist_object_in_question"]
            except KeyError as ke:
                sys.stderr.write("WARNING no control distance found, method will fail.\n")
                sys.stderr.write(str(ke))

    def find_distance(self):
        """
        This method uses the linear relationship of heights to find the distance

        `return` dist - the discovered distance that is the result of the procedure
                dimension[2] - the location of x coordinates that are the far left and right most pixels of difference
                dimension[3] - the location of y coordinates that are the far left and right most pixels of difference
        """
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            ppx_per_meter = self.known_height_px / self.height_object_in_question
            dist = (self.known_height_px / dimensions[0]) * self.known_dist
            return dist, dimensions[2], dimensions[3]
        except Exception as e:
            sys.stderr.write("Linear Method Failed.")
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
            entry = {}
            dist, loc_x, loc_y = c.find_distance()
            entry['Method'] = str(c.__class__.__name__)
            entry['File'] = c.obj_file
            entry['Distance'] = dist
            entry['loc_x'] = loc_x
            entry['loc_y'] = loc_y
            ret.append(entry)
        return ret

def text_on_image(image, text, location=(0, 0), color=(255,255,255)):
    """
    Using ImageDraw, the image can be labeled with a name in the picture

    `image` image to be labeled
    `text` text tobe drawn on image
    `location` the pixel coordinates (x, y) that represent the position at which the text will be drawn
    `color` the color of the text in RGB format of the text being drawn
    """
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text(location, text, color, font=font)
    return img

def apply_distance_as_text(list):
    """
    Method as loop to apply the text to series of images

    `list` the list of images on which the text will be permanently drawn
    `return` the list of images, as pathnames, where the modified images are stored
    """

    directory = os.path.dirname(os.path.realpath(__file__))
    slideshow = []
    for res in list:
        image, text, location = res['File'], str(res['Distance']), res['loc_x']
        im = text_on_image(image, text, location, color=(255, 0, 0))
        im.save(os.path.join(directory, "slideshow", os.path.basename(image)))
        slideshow.append(os.path.join(directory, "slideshow", os.path.basename(image)))
    return slideshow

def parse_args():
    """
    Method to parse args from command sys.args. Uses python.argparser

    `return` args, the list of parsed args as a argparser object
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--known_height_m", type=float, required=True, help="the known height of the object being investigated, in meters")
    ap.add_argument("--methods", nargs='+', required=False, help="(P,S,T,Q, or L) the method(s) chosen to be applied for investigation, if none is chosen default is Linear")
    ap.add_argument("--base", metavar="FILE",
                    required=True, help="base image file for image merge")
    ap.add_argument("--files", nargs='+', metavar="FILE", required=True,
                    help="The list of files to be merged against base, the distance of the highlight in each will be found")
    args = ap.parse_args()
    return args

def run_me(known_height, method_flags, base_file, infiles):
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

    configs = {'P': Primary, 'S': Secondary, 'T': Tertiary, 'Q': Quaternary, 'L': Linear}
    df = Macro()
    for flag in method_flags:
        for obj_file in infiles:
            df.add(configs[flag.upper()](known_height=known_height, obj_file=obj_file, base_file=base_file))

    results = df.run()
    return list(results)

def main(begin_index, end_index, render_sw=None):
    """
    Main method, intended to parse args and perform operation in order

    """
    warnings.filterwarnings('ignore')

    args = parse_args()
    print 'Args:'
    for arg in vars(args):
        print '\t', arg, getattr(args, arg)

    files = args.files
    results = run_me(known_height=args.known_height_m, method_flags=args.methods, base_file=args.base,infiles=files)

    print '\n', color.UNDERLINE, 'Results:', ' ' * 50, color.END, '\n'
    for dict in results:
        key, val = dict.items()[0]
        print color.UNDERLINE, key, ':', val, 'meters', color.END
        for key, val in dict.items()[1:]:
           print '\t', key, ':', val

    directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    folder = os.path.join(directory, 'Distance', 'slideshow')

    images = [f for f in listdir(folder) if isfile(join(folder, f))]
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    # Used to display the 'slide show' of the images that are the result
    import slideshow
    slideshow.slideshow(folder)

    # Open in ms paint as alternative
    # if render_sw is not None:
    #     for file in apply_distance_as_text(results[begin_index:end_index]):
    #         p = subprocess.Popen([render_sw, file])
    #         p.wait()

if __name__ == '__main__':

    # args to be removed after testing
    render_tool = "mspaint.exe"
    begin_index = 0
    end_index = 3

    main(begin_index, end_index, render_tool)
    sys.exit(0)