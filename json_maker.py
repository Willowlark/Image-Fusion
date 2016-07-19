import json
import os

# some useful sensor height to crop factor relations
camera_dict = {'1/3.2': (3.42, 7.6), '1/3.0': (3.6, 7.2), '1/2.6': (4.1, 6.3), '1/2.5' : (4.29, 6.0), '1/2.3': (4.55, 5.6), '1/1.8': (5.32, 4.8), '1/1.7': (5.64, 4.7), '2/3': (6.6, 3.9), '16mm': (7.49, 3.4), '1': (8.80, 2.7), '4/3': (13, 2.0), 'Imax': (52.63, 0.49)}
object_in_question = 0.115

directory = os.path.dirname(os.path.realpath(__file__))

with open(directory + '/result.json', 'w') as fp:
    json.dump(camera_dict, fp)