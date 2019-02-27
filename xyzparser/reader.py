
import os

from xyzparser.trajectory import XYZTrajectory

class XYZReader(object):
    '''Class that reads XYZ trajectory data
    This class currently can be used to read and return
    a complete XYZ trajectory.

    Returns
    -------
    tuple of two numpy arrays of (mx3xn, dtype=np.float64) all `m` atom
    coordinates in `n` frames and (mx1, dtype='s1') all elements
    '''
    def __init__(self):
        super(XYZReader, self).__init__()
        self._filepath = None
        self._file = None
        # TODO config options for reading
        self._len_header = 0
        self._len_frameheader = 2

    def openfile(self, xyzfilepath):
        assert os.path.exists(xyzfilepath)
        self._filepath = xyzfilepath
        self._file = open(xyzfilepath, 'r')

    def readfile(self, xyzfilepath, nframes=None, blocksize=None, stride=None):
        # TODO support blocksize and nframes concurrently
        #       - read blocks until nframes reached
        #       - current nframes only works if less than blocksize
        '''User function for reading file
        This function to be expanded with chunk/stream
        capability using _iterread
        '''
        self.openfile(xyzfilepath)
        self._read(nframes)
        self.closefile()

    def _readblocks(self, framekey, blocksize=None):
        '''This function does actual file reading
        Replace with C code.
        Arguments
        ---------
        framekey :: str pattern indicating top of a new frame
        blocksize :: int number of frames to read between Trajectory object updates
        '''
        def byframe(stopkey):
            frame = list()
            for line in self._file:
                if line.strip() == stopkey:
                    break
                else:
                    frame.append(line.split())
            return frame

        reading = True
        block = list()
        while reading:
            print("Reading now")
            frame = list()
            try:
                firstline = next(self._file).split()
                print("\n\n ON NEWFRAME----------------------------#")
                print("got firstline", firstline)
                frame = byframe(framekey)
                block.append(frame)

                print("blocksize: ", blocksize)
                print("block size: ", len(block))
                print("blocks sizes: ", [len(block) for b in block])
                if blocksize and len(block) == blocksize:
                    print("Giving up from blocksize match")
                    yield block
                    block = list()

            except StopIteration:
                print("StopIteration")
                reading = False

    def _read(self, nframes=None, blocksize=None):
        assert not self._file.closed

        framekey = next(self._file).strip()

        if blocksize is None:
            if nframes is None:
                # read to end in 1 block
                iterblocks = iter(self._readblocks(framekey))
            else:
                # read to nframes in 1 block
                iterblocks = iter([next(self._readblocks(framekey, blocksize=nframes))])
        else:
            if nframes is None:
                # read to end in blocks of size blocksize
                iterblocks = iter(self._readblocks(framekey, blocksize=blocksize))
            else:
                # read to nframes in blocks of size blocksize
                nblocks = bool(nframes%blocksize) + (nframes // blocksize)
                nframes = nframes % blocksize
                iterblocks = iter([next(self._readblocks(framekey, blocksize=blocksize)) for i in range(nblocks-1)]+[self._readblocks(framekey, blocksize=nframes)])

        trajectory = XYZTrajectory()
        for block in iterblocks:
            print("Got block", len(block))
            trajectory.add_frames(block)

    def closefile(self):
        self._file.close()

