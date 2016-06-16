import math
import scipy
from scipy import stats

class ortho_rectification(object):
    """
    this class can encapsulate all of the orth-rectification functionality
    """

    def __init__(self, x, y, know_height):
        """
        constructor for one rectifier

        :param x: list of x values in coordinate pairs
        :param y: list of y values in coordinate pairs
        :param know_height: known height of object being rectified
        """
        self.known_height = know_height
        self.regression = stats.linregress([1/i for i in x],y)

    def find_distance_from_aperture(self, perceived_height):
        """
        This method will return the distance in meters of the object whose height is represented as perceived_height

        :param perceived_height: the height in cm of the object as it is perceived, in comparison to its known height
        :return: Integer result representing the distance in cm of the object from the aperture
        """
        ratio_height = perceived_height / self.known_height
        if  ratio_height > 1.0:         # perceived height cannot exceed 100% of actual height
            raise Exception("perceived size cannot exceed actual height")
        else:
            return ((self.regression[0] * (1 / ratio_height)) + self.regression[1]) * self.known_height

if __name__ == "__main__":

    x = [0.5, 0.25, 0.1225]
    y = [1.1565, 4.1913, 10.8696]
    OR = ortho_rectification(x, y, 177)
    OR1 = ortho_rectification(x, y, 187.16) # + one standard deviation away
    OR2 = ortho_rectification(x, y, 166.84) # - one standard deviation away

    print  "1/2 the size"
    print "control", OR.find_distance_from_aperture(93.58) / 100, OR.find_distance_from_aperture(83.42) / 100
    print "deviated", OR1.find_distance_from_aperture(93.58) / 100, OR2.find_distance_from_aperture(83.42) / 100

    print "1/20 th size"
    print "control", OR.find_distance_from_aperture(9.358) / 100, OR.find_distance_from_aperture(8.342) / 100
    print "deviated", OR1.find_distance_from_aperture(9.358) / 100, OR2.find_distance_from_aperture(8.342) / 100

    print "1/100 the size"
    print "control", OR.find_distance_from_aperture(1.8716) / 100, OR.find_distance_from_aperture(1.6684) / 100
    print "deviated", OR1.find_distance_from_aperture(1.8716) / 100, OR2.find_distance_from_aperture(1.6684) / 100





