class PixelCommand(object):

    def __init__(self):
        pass

    def execute(self, p1, p2):
        pass


class RedHighlightCommand(PixelCommand):

    def execute(self, p1, p2):
        return (255, 0, 0)


class TakeSecondCommand(PixelCommand):

    def execute(self, p1, p2):
        return p2


class ColorDiffCommand(PixelCommand):

    diffnum = 120

    def __init__(self):
        pass

    def execute(self, p1, p2):
        return abs(p1[0] - p2[0]) > self.diffnum \
           or abs(p1[1] - p2[1]) > self.diffnum \
           or abs(p1[2] - p2[2]) > self.diffnum


class PixelRemote(object):

    def __init__(self):
        self.outdata = None
        self.comparedata = None

        self.checkcmd = None
        self.actcmd = None

    def run(self, x1, y1, x2, y2):
        currpixel = self.outdata[x1, y1]
        comparepixel = self.comparedata[x2, y2]
        if self.checkcmd.execute(currpixel, comparepixel):
            self.outdata[x1, y1] = self.actcmd.execute(currpixel, comparepixel)
            return 1
        return 0

    def setCheckCommand(self, command):
        self.checkcmd = command

    def setActorCommand(self, command):
        self.actcmd = command


class ExtractPixelRemote(PixelRemote):

    def __init__(self):
        super(ExtractPixelRemote, self).__init__()
        self.pixels = {}

    def run(self, x1, y1, x2, y2):
        currpixel = self.outdata[x1, y1]
        comparepixel = self.comparedata[x2, y2]
        if self.checkcmd.execute(currpixel, comparepixel):
            ret = self.actcmd.execute(currpixel, comparepixel)
            self.outdata[x1, y1] = ret
            self.pixels[(x1, y1)] = ret
            return 1
        return 0