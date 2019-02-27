
#import numpy as np

class XYZTrajectory(object):
    def __init__(self):
        self._frames = []
        self._atoms = []
        self._trajectory = []
    def add_frames(self, frames_block):
        self._frames.extend(frames_block)
