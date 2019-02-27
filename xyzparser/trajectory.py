
import numpy as np

class XYZTrajectory(object):
    '''
    Attributes
    ----------
    trajectory
        numpy array (nxmx3, dtype=np.float64) of all 3 coordinates
        from `m` atoms in `n` frames
    '''
    def __init__(self):
        super(XYZTrajectory, self).__init__()
        self._frames = []
        self._atoms = [] #TODO self._elements
        self._trajectory = None

    @property
    def atoms(self):
        return self._atoms

    @property
    def trajectory(self):
        '''Get the trajectory as a numpy array
        '''
        if self._trajectory is None:
            self._trajectory = np.concatenate(self._frames)
            del self._frames
            self._frames = []

        return self._trajectory

    def add_frames(self, frames_block):
        coords = lambda atom: atom[1:4]
        atomname = lambda atom: atom[0]
        if not self._frames:
            self._atoms = np.array([ atomname(atom)
              for atom in frames_block[0]], dtype='|S1')

        #frames = np.array([ [coords(atom) for atom in frame]
        #  for frame in frames_block], dtype=np.float64)
        for frame in frames_block:
            for atom in frame:
                print(atom)
                np.array(atom)

        #self._frames.append(frames)

    def __getitem__(self):
        # Navigate list of arrays or
        # build one larger one somewhere?
        raise NotImplementedError

