from __future__ import division
import math
from PIL import Image
from PIL.ExifTags import TAGS

# consult link for more info
#http://photoseek.com/2013/compare-digital-camera-sensor-sizes-full-frame-35mm-aps-c-micro-four-thirds-1-inch-type/

# resource for info on exif tags
#http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html

# more info on this solution
#http://stackoverflow.com/questions/22634518/how-to-get-distance-of-object-from-iphone-camera-using-image-exif-meta-data

dict = {'1/2.5' : (4.29, 6.0), '1/2.3': (4.55, 5.6), '1/1.8': (5.32, 4.8)} # some useful sensor height to crop factor relations
object_in_question = 0.0833 # Real vertical height of object being examined
pixel_pct = 0.33    # precise portion of vertical pixel occupied by object

def get_exif(path_name):
    ret = {}
    i = Image.open(path_name)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def find_focal_length(control_height_m, control_distance_m, known_sensor_height):
    theta = math.atan(control_height_m / control_distance_m)
    focal_len = known_sensor_height / math.tan(theta)
    print "f", focal_len
    return focal_len

def distance_given_height_in_pixels(height_pct, height_of_sensor_mm, focal_len_mm):
    global object_in_question
    theta = math.tan((height_pct * height_of_sensor_mm) / focal_len_mm)  # if height of object is X pct of the pixels, then it must also be X pct of the sensor height in mm
    goal_distance = object_in_question / math.atan(theta)
    return goal_distance

def get_focal_length_given_fnumber(fnumber, diameter_entrance_pupil):
    # https://en.wikipedia.org/wiki/F-number
    return diameter_entrance_pupil * fnumber

if __name__ == "__main__":
    global object_in_question
    global pixel_pct
    try:
        tags = get_exif('C:\Users\Bob S\Desktop\\IMG_0941.jpg')
        print tags

        f = float(tags['LensModel'][22:26])

        print tags['SensingMethod']

        print "f", f
        print "dist", distance_given_height_in_pixels(pixel_pct, dict['1/2.3'][0], f)
    except Exception as e:
        print e
        a = object_in_question # height in meters
        d = 10 # in meters

        f = find_focal_length((a*1000), (d*1000), dict['1/2.3'][0])
        print "dist", distance_given_height_in_pixels(pixel_pct, dict['1/2.3'][0], f)
