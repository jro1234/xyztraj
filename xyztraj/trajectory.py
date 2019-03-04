
import numpy as np


class XYZTrajectory(object):
    '''Interface object to trajectory data

    Attributes
    ----------
    trajectory :: numpy array (nxmx3, dtype=np.float64)
    all 3 coordinates from `m` atoms in `n` frames

    atoms :: numpy array (mx1, dtype='|S1')
    string identifying each atom, currently its just the element
    '''
    def __init__(self):
        super(XYZTrajectory, self).__init__()
        self._frames = []
        self._atoms = None
        # TODO self._elements
        self._trajectory = None

    @property
    def atoms(self):
        return self._atoms

    @property
    def trajectory(self):
        '''Get the trajectory as a numpy array
        '''
        if self._frames:
            if self._trajectory is None:
                self._trajectory = np.concatenate(self._frames)
            else:
                self._trajectory = np.concatenate(
                    [self._trajectory] + self._frames)

            del self._frames
            self._frames = []

        return self._trajectory

    def add_frames(self, frames_block):
        '''Add a block of frames to this trajectory instance
        '''
        coords = lambda atom: atom[1:4]
        atomname = lambda atom: atom[0]

        if self._atoms is None:
            self._atoms = np.array(
                [atomname(atom) for atom in frames_block[0]],
                dtype='|U1')

        frames = np.array([
            [coords(atom) for atom in frame]
            for frame in frames_block],
            dtype=np.float64)

        self._frames.append(frames)

    def __getitem__(self):
        # list-like slice indexing plz!
        # Navigate list of arrays or
        # build one larger one somewhere?
        raise NotImplementedError
