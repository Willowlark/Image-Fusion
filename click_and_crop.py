# import the necessary packages
import argparse, cv2, os, sys
from pprint import pprint

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
image = None

cur_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(cur_dir, 'Output')
file_out = os.path.join(output_dir, 'dump.png')

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, image

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        image = clone.copy()
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", image)

def close_and_exit():
    # close all open windows
    cv2.destroyAllWindows()
    sys.exit(0)

args = None
while True:
    refPt = []
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()

    ap.add_argument("-i", "--input", required=True, help="Path to the input")
    ap.add_argument("-o", "--output", required=False, help="Path to the output")
    ap.add_argument("-s", "--scale", required=False, help="The relative value by which the crop will be increased")

    args = vars(ap.parse_args())

    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread(args["input"])
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)

    # keep looping until the 'q' key is pressed
    while not not True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()

        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break

        elif key == ord("q"):
            close_and_exit()

    # if there are two reference points, then crop the region of interest
    # from the image and display it
    roi = None
    if len(refPt) == 2:
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        x_y = float(args['scale']) if args['scale'] else 1.0
        roi = cv2.resize(roi, (0, 0), fx=x_y, fy=x_y)
        cv2.imshow("ROI", roi)

        key = cv2.waitKey(1) & 0xFF
        if key == cv2.EVENT_LBUTTONDOWN:
            break

    if args["output"]: cv2.imwrite(args["output"], roi)

    pprint(args)

close_and_exit()