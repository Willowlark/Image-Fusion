import sys
import json
import os
from PIL import Image

# JSON of following format
# {
#   "height_object_in_question" : 0.115,
#   "dist_object_in_question" : 1.0,
#   "calibration_image" : "C:\\Users\\Bob S\\PycharmProjects\\Image-Fusion\\Input\\IMG_0942.jpg"
# }

directory = os.path.dirname(os.path.realpath(__file__))
calibration_image = sys.argv[1]
height_object_in_question = sys.argv[2]
dist_object_in_question = sys.argv[3]

with open(directory + '\\json\\calib_info.json', 'w') as fp:
    json.dump({"height_object_in_question" : height_object_in_question,
                "dist_object_in_question" : dist_object_in_question,
                "calibration_image" : calibration_image}, fp, indent=4)


with open(directory + '\\json\\calib_info.json', 'r') as fp:
    json_data = json.load(fp)
    im = Image.open(json_data["calibration_image"])
    print "obj height", json_data["height_object_in_question"]
    print "obj distance", json_data["dist_object_in_question"]
    im.show()


