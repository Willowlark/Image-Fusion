# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2

def execute(inImage, inTemplate):
    """
    `Author`: Bill Clark, Adrian Rosebrock

    Inspired by the code located here:
    http://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
    This module implements template matching from opencv. What this does is takes an image to
    use as a template. That image is identified inside of another image which contains a
    smaller sample of the template. The template maybe any size SMALLER than the image that contains
    it. This is more advanced than typical template matching because we reduce the template on
    a scale. This allows us to find smaller versions of the template in the image, such as a zoomed
    in image's location on a zoomed out of the same subject. This can be seen with input zoom.jpg
    and out.jpg.

    `inImage`: The image to look for the template in.

    `inTemplate`: The template to look for in the image.
    """
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--template", required=True, help="Path to template image")
    ap.add_argument("-i", "--image", required=True,
        help="Path to images where template will be matched")
    ap.add_argument("-v", "--visualize",
        help="Flag indicating whether or not to visualize each iteration")
    args = vars(ap.parse_args())

    if not inImage: image = cv2.imread(args["image"])
    else: image = cv2.imread(inImage)
    origimage = image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.Canny(image, 50, 200)

    if not inTemplate: template = cv2.imread(args["template"])
    else: template = cv2.imread(inTemplate)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    (origTW, origTH) = template.shape[:2]
    found = None

    for scale in np.linspace(0.28, 1.0, 20)[::-1]:
        resized = imutils.resize(template, width = (int(template.shape[1]*scale)))
        # r = template.shape[1] / float(resized.shape[1])
        (tW, tH) = resized.shape[:2]

        # if resized.shape[0] < image.shape[0] or resized.shape[1] < image.shape[1]:
        #     break

        edged = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(image, edged, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        print resized.shape[:2], maxLoc[:2], maxVal

        if args.get("visualize", False):
            clone = np.dstack([image, image, image])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            # cv2.waitKey(0)

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, 1, tW, tH)
        print found[0], '\n'

    (_, maxLoc, r, tW, tH) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    cv2.rectangle(origimage, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.imshow("Image", origimage)
    cv2.waitKey(0)

if __name__ == "__main__":
    execute(None, None)