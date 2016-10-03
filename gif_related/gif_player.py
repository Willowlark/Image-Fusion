from Tkinter import *
from PIL import Image, ImageTk

"""
This file is leveraged from a public source to generate a tkinter label that visualizes an animated gif

code adapted from source solution at:
http://stackoverflow.com/questions/28518072/play-animations-in-gif-with-tkinter

Used by homography.py class for gif displaying.
By extending tkinter's label, we can apply the extended use of illustration to moving images.
self.frames stores the Image.tk.photoimages that are sequenced over based on the duration variable created animation.
"""

class gif_player(Label):

    def __init__(self, root, filename, duration=None):
        """
        constructor for gifPlayer object

        `master` root pane of window
        `filename` .gif file to be opened adn displayed
        `duration` delay between frames, in seconds
        """
        self.root = root
        self.filename = filename
        self.duration = duration
        self.start(self.root, self.filename, self.duration)

    def start(self, root, filename, duration=None):
        """
        run instance gifPlayer
        """
        self.im = Image.open(filename)
        seq =  []
        try:
            while 1:
                seq.append(self.im.copy())
                self.im.seek(len(seq)) # skip to next frame
        except EOFError:
            pass # we're done

        if duration is None:
            try:
                self.delay = self.im.info['duration']
            except KeyError:
                self.delay = 100
        else:
            self.delay = int(duration)

        self.frames = [ImageTk.PhotoImage(seq[0].convert('RGBA'))]

        for image in seq[1:]:
            self.frames.append(ImageTk.PhotoImage(image.convert('RGBA')))

        Label.__init__(self, root, image=self.frames[0])
        self.idx = 0
        self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.frames[self.idx % len(self.frames)])
        self.idx += 1
        self.cancel = self.after(self.delay, self.play)

    def ffwd(self):
        self.play()

    def slow(self):
        self.after_cancel(self.cancel)

    def run(self, root=None):
        """
        stand alone run-me for gifPlayer usage
        """
        if root is None:
            Button(self.root, text='slow down', command=self.slow).pack()
            Button(self.root, text='speed up', command=self.ffwd).pack()
            self.root.mainloop()
        else:
            Button(root, text='slow down', command=self.slow).pack()
            Button(root, text='speed up', command=self.ffwd).pack()
            root.mainloop()

if __name__ == "__main__":
    """
    main test for gif playing application

    example:
    sys.argv[1] = "gif_test/my_gif.gif"
    """

    file = sys.argv[1]
    player = gif_player(Tk(), file)
    player.pack()
    player.run()