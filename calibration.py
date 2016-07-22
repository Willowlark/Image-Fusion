import sys
import json
import os
import math
from PIL import Image

# JSON of following format
# {
#   "height_object_in_question" : 0.115,
#   "dist_object_in_question" : 1.0,
#   "calibration_image" : "C:\\Users\\Bob S\\PycharmProjects\\Image-Fusion\\Input\\IMG_0942.jpg"
#   "focal_len": 278.2608695652174,
# }

def parse_args():
    global calibration_image
    global height_object_in_question
    global dist_object_in_question
    calibration_image = sys.argv[1]
    height_object_in_question = sys.argv[2]
    dist_object_in_question = sys.argv[3]

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
    # print "img dimensions", img_width, "x", img_height, "px"

    return obj_height_px, img_height

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
    return focal_len_px


# running methods
parse_args()

object_height_px = get_object_px(calibration_image)[0]

focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)

directory = os.path.dirname(os.path.realpath(__file__))
calib_file = os.path.join(directory, 'json', 'calib_info.json')

with open(calib_file, 'w') as fp:
    json.dump({"height_object_in_question" : float(height_object_in_question),
                "dist_object_in_question" : float(dist_object_in_question),
                "calibration_image" : calibration_image,
               "focal_len" : float(focal_len)}, fp, indent=4)


with open(calib_file, 'r') as fp:
    json_data = json.load(fp)
    im = Image.open(json_data["calibration_image"])
    print "obj height", json_data["height_object_in_question"]
    print "obj distance", json_data["dist_object_in_question"]
    print "focal len", json_data["focal_len"]
    # im.show()

print "calibration finished", calib_file

sys.exit(0)


