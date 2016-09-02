from __future__ import division
import sys, json, os, math
from PIL import Image
import Console
from pprint import pprint

"""
The main function of this script will write to the fixed location file, json/calib_info.json, the information pertinent to the distance_finder.py module
By running the main script on the example arguments specified below will yield the calib_json file to store the focal_length info to be accessed by distance_finder.py.

Example ARGS:
"C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_base.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_calib.jpg" 0.124 1.0

...produces JSON of following format:
{
    "calibration_image": "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_calib.jpg",
    "height_object_in_question": 0.124,
    "focal_len": 556.4516129032259,
    "base_image": "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_base.jpg",
    "dist_object_in_question": 1.0
}

  <OR>

Example ARGS:
69 0.124 1.0
...produces JSON of following format:
{
    "height_object_in_question": 0.124,
    "focal_len": 556.4516129032259,
    "dist_object_in_question": 1.0
}
"""

def find_object_px(base_file, obj_file):
    """
    This method will be find the height of the found object in pixels
    to be used essential to every distance method

    `return` the object height in pixels, as determined by the Image_merge module via console
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

    return first.height

def calibrate_focal_len(control_object_distance, control_object_height, control_object_height_px):
    """
    this method will find the necessary value for focal length using the founding principles of similar angles applied using trigonometry
    When the known distance of the object, and the fixed, known height of the object are used to calibrate for the arbitrary angle, control angle
    they can be used to find the focal length, assuming the same percent of the sensor is occupied by the object as is occupied in the photograph

    `control_object_distance` the fixed, measured distance used for calibration
    `control_object_height_px` the fixed, measured height in pixels of teh object's visage in the digital photo
    `return` focal length in pixels
    """
    control_angle = math.atan(float(control_object_height) / float(control_object_distance))  # achieve theta for this controlled case
    focal_len_px = control_object_height_px / math.tan(control_angle)
    print "focal len found,", focal_len_px, "px"
    return focal_len_px

def run_me():
    """
    run me of main script.
    Opens, calculates ad writes to calib_info

    """
    print "Calibrating focal length"

    global dist_object_in_question
    global height_object_in_question
    global object_height_px

    # running methods
    if len(sys.argv) > 4:
        base_image = sys.argv[1]
        calib_image = sys.argv[2]
        height_object_in_question = float(sys.argv[3])
        dist_object_in_question = float(sys.argv[4])    # get args from command line, see example args at top of file

        object_height_px = find_object_px(base_image, calib_image)

        focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)   # find focal len px

        directory = os.path.dirname(os.path.realpath(__file__))
        calib_file = os.path.join(directory, 'json', 'calib_info.json') # destination of calibration storage

        with open(calib_file, 'w') as fp:   # write all pre-conditions and focal len post-condition to calib_file
            json.dump({"height_object_in_question" : height_object_in_question,
                        "dist_object_in_question" : dist_object_in_question,
                       "base_image" : base_image,
                        "calibration_image" : calib_image,
                       "focal_len" : focal_len,
                       "control_object_height_px" : object_height_px}, fp, indent=4)

    else:
        object_height_px = float(sys.argv[1])
        height_object_in_question = float(sys.argv[2])
        dist_object_in_question = float(sys.argv[3])

        focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)   # find focal len px

        directory = os.path.dirname(os.path.realpath(__file__))
        calib_file = os.path.join(directory, 'json', 'calib_info.json') # destination of calibration storage

        with open(calib_file, 'w') as fp:   # write all pre-conditions and focal len post-condition to calib_file
            json.dump({"height_object_in_question" : height_object_in_question,
                        "dist_object_in_question" : dist_object_in_question,
                        "focal_len" : focal_len}, fp, indent=4)

    print "calibration finished, see", calib_file

if __name__ == "__main__":
    run_me()
    sys.exit(0)


