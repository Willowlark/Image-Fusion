import argparse
import ImageMerge
import PixelProcess
import peopledetect
import cmd
import re

class Console(cmd.Cmd):

    def __init__(self, output):
        cmd.Cmd.__init__(self)
        self.groups = None
        self.m = ImageMerge.Merger(output)
        self.prompt = '> '

    def do_merge(self, images):
        """Merge any number of images."""
        self.m.merge(images)
    def do_testmerge(self, images):
        """Merge any number of images, then reset to before the merge."""
        self.m.testMerge(images)
    def do_exportmerge(self, images):
        """Merge any number of images, save to the outfile, and reset the state."""
        paths = self.splitPaths(images)
        self.m.exportMerge(paths[0], *paths[1:])
    def do_mergeas(self, images):
        """Change the outfile to a new one, then merge any number of images."""
        paths = self.splitPaths(images)
        self.m.mergeAs(paths[0], *paths[1:])

    def do_redhighlight(self, arg):
        """When a pixel is checked true, make it red."""
        self.m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    def do_takesecond(self, arg):
        """When a pixel is checked true, make it the new pixel."""
        self.m.processor.setActorCommand(PixelProcess.TakeSecondCommand())
    def do_colordiff(self, checknum):
        """Check a pair of pixels as true if the color difference is less than <number>."""
        self.m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())
        if checknum: self.m.processor.checkcmd.diffnum = int(checknum)
        else: self.m.processor.checkcmd.diffnum = 0
    def do_resetcommands(self, arg):
        """Set the check and act commands to empty commands."""
        self.m.processor.setActorCommand(PixelProcess.PixelCommand())
        self.m.processor.setCheckCommand(PixelProcess.PixelCommand())

    def do_extractremote(self, arg):
        """Set the processor's remote to record changed pixels."""
        self.m.processor = PixelProcess.ExtractPixelRemote()
    def do_regularremote(self, arg):
        """Set the remote to a basic one."""
        self.m.processor = PixelProcess.PixelRemote()

    def do_gengroups(self, arg):
        if isinstance(self.m.processor, PixelProcess.ExtractPixelRemote) \
          and self.m.processor.pixels is not None:
            self.groups = self.m.processor.getGroupedPixels()
    def do_showgroups(self, arg):
        if self.groups:
           for group in self.groups.generator():
               print group
    def do_filtergroups(self, arg):
        if self.groups: self.groups.filter()
    def do_countsortgroups(self, arg):
        if self.groups: self.groups.sortCount()
    def do_ratiosortgroups(self, arg):
        if self.groups: self.groups.sortRatio()
    def do_savefirstgroup(self, path):
        if not path: print 'Specify the save path.'
        if self.groups and path: self.groups.first().save(path, self.m.processor.pixels)

    def do_detect(self, images):
        """Detect people in any number of images."""
        paths = self.splitPaths(images)
        peopledetect.detect(paths)

    def do_save(self, arg):
        """Save the image."""
        self.m.save()
        print self.m.outfile
    def do_show(self, arg):
        """Show the image."""
        self.m.show()

    def splitPaths(self, string):
        return re.findall('([^ ][^.]*\..{3})', string)

if __name__ == "__main__":
    con = Console('Output\ImFuse.jpg')
    con.onecmd('?')
    con.cmdloop()

