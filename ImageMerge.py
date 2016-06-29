from PIL import Image

debug = 0


class Merger():

    def __init__(self, outfile):
        """
        `Author`: Bill Clark

        This class is basically the same method as mergemodeRGB, now the contained mergeAll method.
        The add method is almost identical. The reason for this class is that it allows for urls to be
        added incrementally with ease. Given an instance where you want to merge urls to the same outfile
        based off the same base image, but don't have the urls all at once, this method allows for any number
        of add calls to merge images to the output. This comes with over head, saving the image to the
        outfile location after each individual merge, but certain situations really need this kind of functionality.

        `outfile`: The file address to save the output file to.

        `base`: The unmodified image which all the layers will be drawn to. The images MUST line up, which is why
            the center and zoom are REQUIRED. Those parameters being the same will line up the unchanged pixels
            correctly so that only the edited pixels pick up as different.
        """

        self.initialized = 0
        self.autoSave = 0

        self.outfile = outfile
        self.outdata = None

        self.checker = PixelChecker()
        self.actor = PixelActor()
        self.mergedFiles = []

    def setup(self, file):
        """

        :param file:
        :return:
        """
        self.outimage = Image.open(file)
        self.outdata = self.outimage.load()
        if self.autoSave: self.save()
        self.initialized = 1

    def merge(self, *images):
        """
        `Author`: Bill Clark

        This merges a list of images, with layers of paths and markers, on top of a plain base image. It will then
        output the merged image to the outfile provided. This method only works with images encoded in RGB color,
        which is expected of it's inputs. The method works by creating a new file for the changes, and opening the base
        and a layer. Each pixel in the base is compared with the layer, if they're different enough the layer pixel is
        placed over the original base image pixel that was contained in the new file. This is done for every pixel and
        every layer. Debug information contains the ratio of different to not different pixels in percent form, as well
        as a display of the output after each layer merge.

        `images`: Any number of image urls that are layers of the base image. Same center and zoom are a must.
        """

        if not self.initialized:
            self.setup(images[0])
            images = images[1:]

        if len(images) > 0:
            for image in images:
                changed = self.checkAndAct(image)

            self.mergedFiles.append(image)
            if debug: self.printDiffSame(changed)

        if debug: self.show()
        if self.autoSave: self.save()
        
    def testMerge(self, *images):
        """
        `Author`: Bill Clark

        This merges a list of images, with layers of paths and markers, on top of a plain base image. It will then
        output the merged image to the outfile provided. This method only works with images encoded in RGB color,
        which is expected of it's inputs. The method works by creating a new file for the changes, and opening the base
        and a layer. Each pixel in the base is compared with the layer, if they're different enough the layer pixel is
        placed over the original base image pixel that was contained in the new file. This is done for every pixel and
        every layer. Debug information contains the ratio of different to not different pixels in percent form, as well
        as a display of the output after each layer merge.

        `images`: Any number of image urls that are layers of the base image. Same center and zoom are a must.
        """
            
        orig = self.outimage.copy()
        state = self.autoSave

        self.autoSave = 0
        self.merge(*images)
        self.autoSave = state

        self.outimage = orig
        self.outdata = self.outimage.load()

    def exportMerge(self, outfile, *images):
        """
        `Author`: Bill Clark


        """

        orig = self.outimage.copy()
        state = self.autoSave

        self.autoSave = 0
        self.merge(*images)
        self.autoSave = state

        self.save(self.outfile, outfile)

        self.outimage = orig
        self.outdata = self.outimage.load()

    def mergeAs(self, outfile, *images):
        """
        `Author`: Bill Clark

        This method will change the color of any pixel that is different between the base image and another provided
        image. This works in the same way as mergeRGB, which does mean the inputs need to be RGB format. You can use
        this to visually see the detected differences between two images.

        `images`: the image to compare to base.

        `outfile`: The file to write the color marked image to.
        """

        self.outfile = outfile
        self.merge(*images)

    def checkAndAct(self, img):
        """

        :param img:
        :return:
        """
        compareimage = Image.open(img)
        comparedata = compareimage.load()

        counter = 0
        for x in range(self.outimage.size[0]):
            for y in range(self.outimage.size[1]):
                currpixel = self.outdata[x, y]
                comparepixel = comparedata[x, y]
                if self.checker.check(currpixel, comparepixel):
                    self.outdata[x, y] = self.actor.act(currpixel, comparepixel)
                    counter += 1
        return counter

    def convert(self, *images):
        """
        `Author`: Bill Clark

        This method takes any number of images and converts the from P color mode to RGB mode. RGB is required by the
        merge methods above. The files are saved to a different file, same prefix, but .con being placed at the end.

        `images`: The images that need to be converted. They are expected to be in P color mode, though other modes
                may convert cleanly.

        `return`: A list of the new file locations, since the file names have been changed.
        """
        ret = []
        count = 0
        for image in images:
            img = Image.open(image)
            im = img.convert("RGBA")

            split = image.split('/')
            path = '/'.join(split[:-1]) + '/Converts/' + ''.join(split[-1:])

            ret.append(path)
            im.save(path)
            count += 1
        return ret

    def show(self, image=None):
        if not image: image = self.outimage
        image.show()

    def save(self, image=None, outfile=None):
        if not image: image = self.outimage
        if not outfile: outfile = self.outfile
        image.save(outfile)

    def printDiffSame(self, counter):
        """

        :param counter:
        :return:
        """
        print "Different Pixels:", counter, repr(round((counter/360000.)*100,2)) + '%', " Same Pixels:", \
            360000-counter, repr(round(((360000-counter)/360000.)*100,2)) + '%'+ '\n'


class PixelChecker:
    def __init__(self,):
        self.diffnum = 120

    def check(self, p1, p2):
        self.check = self.colorDiffGreater
        return self.check()

    def colorDiffGreater(self, p1=None, p2=None):
        if p1 and p2:
            return abs(p1[0] - p2[0]) > self.diffnum \
                   or abs(p1[1] - p2[1]) > self.diffnum \
                   or abs(p1[2] - p2[2]) > self.diffnum
        else:
            self.check = self.colorDiffGreater


class PixelActor:
    def __init__(self):
        pass

    def act(self, p1, p2):
        self.act = self.redHighlight()
        return self.act()

    def redHighlight(self, p1=None, p2=None):
        if p1 and p2:
            return (255, 0, 0, 255)
        else:
            self.act = self.redHighlight

    def takeNew(self, p1=None, p2=None):
        if p1 and p2:
            return p2
        else:
            self.act = self.takeNew


if __name__ == "__main__":
    debug = 1
    inputs = ['Input/One Visual.jpg', 'Input/One Infrared.jpg']
    m = Merger('Output/ImF.png')

    m.actor.takeNew()
    m.merge(inputs[0])
    m.merge(inputs[1])

    m.actor.redHighlight()
    m.checker.diffnum = 30
    m.mergeAs('Output/DifferenceFile.png', 'Output/One Fused Provided.jpg')
    m.save()