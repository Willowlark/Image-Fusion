import cv2, itertools
from os import listdir
from os.path import isfile, join

class slideshow():

    def __init__(self, folder):
        if isinstance(folder, basestring):
            images = [f for f in listdir(folder) if isfile(join(folder, f))]
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)

            done = False
            for image in itertools.cycle(images):

                img = cv2.imread(folder + "/" + image)
                cv2.imshow('image', img)

                while True:
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("f") or key == ord('\n'):
                        break

                    if key == ord("q"):
                        cv2.destroyAllWindows()
                        done = True
                        break
                if done:
                    break
        else:
            done = False
            for image in itertools.cycle(folder):

                cv2.imshow('image', image)

                while True:
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord("f") or key == ord('\n'):
                        break

                    if key == ord("q"):
                        cv2.destroyAllWindows()
                        done = True
                        break
                if done:
                    break


