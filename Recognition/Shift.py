import numpy as np
from PIL import Image

def tupleCompare(t, tt):
    """
    `Author`: Bill Clark

    Finds the difference of each RGB value in two pixels. The difference has to be
    greater than 10 to fail.

    `t`: The first pixel to compare.

    `tt`: The second to compare.

    `return`: False if the difference between any RGB is greater than 5, else true.
    """
    score = 0
    for one, two in zip(t, tt):
        if abs(one - two) < 10:
            score+=1
    return score


def main(image1, image2, accuracy=3, centers=5):
    # Accuracy is the number of pixels to check out from the center point, in each direction.
    # Centers is the number of center points to check on each access, so centers^2 points are chosen.
    #load images
    im1 = Image.open(image1)
    im2 = Image.open(image2)
    data1 = im1.load()
    data2 = im2.load()

    visualize = True # Draws data.

    #find maxX and maxY (Max as in safe max, not highest
    maxX = min(im1.size[0], im2.size[0])-1
    maxY = min(im1.size[1], im2.size[1])-1

    score = []  # Holds the scores for each check. a

    # Iterate over the center points in the image to check around.
    for centerX in np.linspace(accuracy*2, maxX-accuracy*2+1, centers): #accuracy*2 is used to buffer borders
        rowscore = []
        for centerY in np.linspace(accuracy*2, maxY-accuracy*2+1, centers):
            # print 'Center: ', centerX, centerY
            graph = []

            # Iterate over the area around the center and compare the image data to find the shift likelyhood.
            for j in range(-accuracy, accuracy+1):
                graphrow = []
                for i in range(-accuracy, accuracy+1):
                    tup = data1[centerX, centerY]
                    bonus = tupleCompare(tup, data2[centerX+i,centerY+j])
                    graphrow.append(bonus)
                graph.append(graphrow)
            rowscore.append(graph)
        score.append(rowscore)

    # Initalize an array to hold the totals of the scores.
    totals = [[0]*(accuracy*2+1) for x in range(0, len(score[0][0]))]

    # Iterate over score graphs, making the total graph and displaying.
    for row in score:  # Row as in row of score graphs. Number of center points checked.
        for j in range(0, (accuracy*2+1)):  # accuracy^2+1 is the number of columns
                for i in range(0, len(row)):
                    for x in range(0, len(row[i][j])):  # numbers in the row.
                        totals[j][x] += row[i][j][x]
                    if visualize: print row[i][j],
                if visualize: print ''
        if visualize: print ""

    # Iterate over the totals graph to find the highest match value.
    highest = (0,0,0)
    for j in range(0, (accuracy*2+1)):
        for i in range(0, len(totals)):
            if highest[2] < totals[i][j]:
                highest = (i,j,totals[i][j])
            if visualize: print totals[i][j],
        if visualize: print ''

    # Display the highest values and calculate the estimated shift.
    totalcenter = (accuracy*2+1) /2
    highest = (repr(highest[0]-totalcenter), repr(highest[1]-totalcenter), repr(highest[2]))
    print "Closest Shift:", '('+highest[0]+','+highest[1]+')', 'Score:', highest[2]+'/'+ repr(centers**2 * 3)

if __name__ == "__main__":
    main('Input/gsc.jpg', 'Input/gsc shift.jpg')
