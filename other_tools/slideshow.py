import os, sys, cv2, itertools
from os import listdir
from os.path import isfile, join

directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
folder = os.path.join(directory, 'Distance', 'slideshow')

images = [f for f in listdir(folder) if isfile(join(folder, f))]
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

images = itertools.cycle(images)
for image in images:

    img = cv2.imread(folder+"/"+image)
    cv2.imshow('image',img)

    while True:
        key = cv2.waitKey(1) & 0xFF

        if key == ord("f") or key == ord('\n'):
            break

        if key == ord("q"):
            cv2.destroyAllWindows()
            sys.exit(0)
