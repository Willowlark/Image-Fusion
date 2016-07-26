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

    def getGroupedPixels(self):

        groups = []
        processed = []

        for point in self.pixels:
            if point not in processed: explore = [point]
            else: continue

            subprocess = []

            while explore:
                e = explore.pop()
                subprocess.append(e)

                nearby = (e[0]+1, e[1]), \
                         (e[0]-1, e[1]), \
                         (e[0], e[1]+1), \
                         (e[0], e[1]-1)  # E,W,S,N points.

                explore.extend([n for n in nearby if n not in subprocess and n not in explore and n in self.pixels])
            processed.extend(subprocess)
            groups.append(PixelGroup(subprocess))
            # groups.append(subprocess)
        return groups


class PixelGroup(object):

    def __str__(self):
        return repr(self.x)+' '+repr(self.y)+' '+repr(self.height)+' '+repr(self.width)+' '+repr(self.ratio)+'%'

    def __init__(self, groups):
        self.pixels = groups
        self.x, self.y, self.height, self.width, self.ratio = self._size()

    def _size(self):

        if len(self.pixels) <= 1:
            p = [self.pixels[0]]
            return p, p, 1, 1, 100

        x = []
        y = []

        sort = sorted(self.pixels, key=lambda x: x[0])
        x.append(sort[0][0])
        x.append(sort[-1][0])
        sort = sorted(self.pixels, key=lambda x: x[1])
        y.append(sort[0][1])
        y.append(sort[-1][1])

        w = (x[1]-x[0])+1
        h = (y[1]-y[0])+1
        ratio = int((len(self.pixels) / float(w*h))*100)

        return x, y, h, w, ratio