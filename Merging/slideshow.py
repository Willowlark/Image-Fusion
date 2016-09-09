import cv2, itertools
import numpy, sys

class slideshow():

    def __init__(self, files):

        done = False
        for image in itertools.cycle(files):

            cv2.imshow('image', cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))

            while True:
                key = cv2.waitKey(1) & 0xFF

                if key == ord("f") or key == ord('n'):
                    break

                if key == ord("q") or cv2.getWindowProperty('image', 0) < 0:
                    cv2.destroyAllWindows()
                    done = True
                    break

            if done:
                break


