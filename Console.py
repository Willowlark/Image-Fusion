import argparse
import ImageMerge
import PixelProcess
import sys
import cmd

class Console(cmd.Cmd):

    def __init__(self, output):
        cmd.Cmd.__init__(self)
        self.groups = []
        self.m = ImageMerge.Merger(output)
        self.prompt = '> '

    def do_merge(self, *images):
        """Merge any number of images."""
        self.m.merge(*images)
    def do_testMerge(self, *images):
        """Merge any number of images, then reset to before the merge."""
        self.m.testMerge(*images)
    def do_exportMerge(self, outfile, *images):
        """Merge any number of images, save to the outfile, and reset the state."""
        self.m.exportMerge(outfile, *images)
    def do_mergeAs(self, outfile, *images):
        """Change the outfile to a new one, then merge any number of images."""
        self.m.mergeAs(outfile, *images)

    def do_redHighlight(self, arg):
        """When a pixel is checked true, make it red."""
        self.m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    def do_takeSecond(self, arg):
        """When a pixel is checked true, make it the new pixel."""
        self.m.processor.setActorCommand(PixelProcess.TakeSecondCommand())
    def do_colorDiff(self, checknum):
        """Check a pair of pixels as true if the color difference is less than <number>."""
        self.m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())
        self.m.processor.checkcmd.diffnum = int(checknum)
    def do_resetCommands(self, arg):
        """Set the check and act commands to empty commands."""
        self.m.processor.setActorCommand(PixelProcess.PixelCommand())
        self.m.processor.setCheckCommand(PixelProcess.PixelCommand())

    def do_extractRemote(self, arg):
        """Set the processor's remote to record changed pixels."""
        self.m.processor = PixelProcess.ExtractPixelRemote()
    def do_regularRemote(self, arg):
        """Set the remote to a basic one."""
        self.m.processor = PixelProcess.PixelRemote()

    def do_showgroup(self, arg):
        if isinstance(self.m.processor, PixelProcess.ExtractPixelRemote) \
          and self.m.processor.pixels is not None:
            self.groups = self.m.processor.getGroupedPixels()


    def do_save(self, arg):
        """Save the image."""
        self.m.save()
    def do_show(self, arg):
        """Show the image."""
        self.m.show()

if __name__ == "__main__":
    con = Console('Output\ImFuse.jpg')
    con.onecmd('?')
    con.cmdloop()

