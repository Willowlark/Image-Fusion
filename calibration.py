from __future__ import division
import sys
import json
import os
import math
from pixel_height_finder import pixel_height_finder
from PIL import Image
import PixelProcess
import ImageMerge

# ARGS:
# "C:\\Users\\Bob S\\PycharmProjects\\Image-Fusion\\Input\\IMG_0971.jpg" 0.291 1.0
#

# JSON of following format
# {
#   "height_object_in_question" : 0.115,
#   "dist_object_in_question" : 1.0,
#   "calibration_image" : "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_0942.jpg"
#   "focal_len": 278.2608695652174,
# }

def parse_args():
    global calibration_image
    global height_object_in_question
    global dist_object_in_question
    calibration_image = sys.argv[1]
    height_object_in_question = sys.argv[2]
    dist_object_in_question = sys.argv[3]

def find_object_px(path, color):
    """
    This method should will be finished to find the height of the found object in pixels
    to be used essential to every distance method

    `path` the path to the image file being investigated
    `color` the color that you sih to look for in the file of path
    `return` (obj_height, img_height) the height of teh object in px, and the height of the image in pixels
    """

    # TODO it is here the procedure of image merging belongs
    # phf = pixel_height_finder(color)
    # out = phf.pixel_write(path).rotate(-90)
    # out.show()
    # res = phf.find_height(out)

    res = deploy_image_merge()
    print "obj height px", res[0], "\nvert px pct", res[1]
    return res

#TODO refactor this method into some useful format
def deploy_image_merge():
    inputs = ['Input/IMG_0971.jpg', 'Input/IMG_0972.jpg']
    m = ImageMerge.Merger('Output/ImF.png')

    m.processor = PixelProcess.ExtractPixelRemote()
    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())

    m.merge(inputs[0])
    m.merge(inputs[1])
    print "Number of pixels recorded.", len(m.processor.pixels)

    post = m.processor.getGroupedPixels()

    print post[0], "W", post[0].width, "H", post[0].height
    ratio = post[0].height / Image.open(inputs[0]).height
    print "RATIO", ratio
    return (post[0].height, ratio)

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

# running methods
parse_args()    # get args from command line, see example args at top of file

colour = (249, 24, 0) # red, the color chosen to be examine d for
object_height_px = find_object_px(calibration_image, colour)[0]

focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)   # find focal len px

directory = os.path.dirname(os.path.realpath(__file__))
calib_file = os.path.join(directory, 'json', 'calib_info.json') # destination of calibration storage

with open(calib_file, 'w') as fp:   # write all pre-conditions and focal len post-condition to calib_file
    json.dump({"height_object_in_question" : float(height_object_in_question),
                "dist_object_in_question" : float(dist_object_in_question),
                "calibration_image" : calibration_image,
               "focal_len" : float(focal_len)}, fp, indent=4)

print "calibration finished", calib_file

sys.exit(0)


