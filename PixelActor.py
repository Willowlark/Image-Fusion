class PixelActor(object):
    def __init__(self):
        """
        `Author`: Bill Clark

        This class conditions to check before acting and contains actions that will be performed on
        any pixel pair that were checked true by the checker. This class is required by Merger.
        All inputs should be pixel tuples, which
        are in the format of (R,G,B,Alpha).
        """
        self.vars = {'outdata': None, 'comparedata': None}

    def act(self, p1, p2):
        """
        `Author`: Bill Clark

        Acts on a pair of pixels.

        `p1`: First pixel to compare.

        `p2`: Second pixel to compare.

        `return`: What the output data's pixel should be assigned to.
        """
        pass

    def check(self, p1, p2):
        """
        `Author`: Bill Clark

        Checks a pair of pixels.

        `p1`: First pixel to compare.

        `p2`: Second pixel to compare.

        `return`: Returns a boolean value indicating if the pixels should be acted on.
        """
        pass

    def run(self, x1, y1, x2, y2):
        currpixel = self.varAccess('outdata')[x1, y1]
        comparepixel = self.varAccess('comparedata')[x2, y2]
        if self.check(currpixel, comparepixel):
            self.varAccess('outdata')[x1, y1] = self.act(currpixel, comparepixel)
            return 1
        return 0

    def varAccess(self, var, new=None):
        if new:
            self.vars[var] = new
        else:
            return self.vars[var]


class PixelDecorator(PixelActor):

    def __init__(self, actor):
        self.actor = actor

    def check(self, p1, p2):
        return self.actor.check(p1, p2)

    def act(self, p1, p2):
        return self.actor.act(p1, p2)

    def varAccess(self, var, new=None):
        return self.actor.varAccess(var, new)


class RedHighlightActor(PixelDecorator):

    def act(self, p1, p2):
        return (255, 0, 0)


class SecondPixelActor(PixelDecorator):

    def act(self, p1, p2):
        return p2


class ColorDiffChk(PixelDecorator):

    def __init__(self, actor):
        super(ColorDiffChk, self).__init__(actor)
        self.varAccess('diffnum', 120)

    def check(self, p1, p2):
        return abs(p1[0] - p2[0]) > self.varAccess('diffnum') \
           or abs(p1[1] - p2[1]) > self.varAccess('diffnum') \
           or abs(p1[2] - p2[2]) > self.varAccess('diffnum')


class ExtractDeco(PixelDecorator):

    def __init__(self, actor):
        super(ExtractDeco, self).__init__(actor)
        self.pixels = []

    def check(self, p1, p2):
        pass


    def act(self, p1, p2):

        pass