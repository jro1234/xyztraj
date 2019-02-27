
import os

from itertools import chain

from xyzparser.trajectory import XYZTrajectory


class blockReadIterator(object):
    '''Class that executes a read function when iterated
    '''
    pass


class XYZReader(object):
    '''Class that reads XYZ trajectory data
    This class currently can be used to read and return
    a complete XYZ trajectory.
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
        # TODO stride
        '''User function for reading file

        Arguments
        ---------
        framekey :: str pattern indicating top of a new frame
        blocksize :: int number of frames to read between Trajectory object updates
        stride :: int read every nth frame given by stride

        Returns
        -------
        XYZTrajectory instance
        '''
        self.openfile(xyzfilepath)
        trajectory = self._read(nframes, blocksize)
        self.closefile()

        return trajectory

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
                print("blocks sizes: ", [len(b) for b in block])
                if blocksize and len(block) == blocksize:
                    print("Giving up from blocksize match\n\n")
                    yield block
                    block = list()

            except StopIteration:
                print("StopIteration")
                reading = False

    def _read(self, nframes=None, blocksize=None):
        assert not self._file.closed

        framekey = next(self._file).strip()
        iterblocks = self._build_iterator(framekey, nframes, blocksize)
        print("iterblocks: {}".format(iterblocks))
        trajectory = XYZTrajectory()

        # TODO replace with blockReadIterator
        #      - then can remove parathesis in for loop
        for block in iterblocks():
            print("Got block", len(block))
            trajectory.add_frames(block)

        return trajectory

    def closefile(self):
        self._file.close()

    # TODO replace with blockReadIterator
    def _build_iterator(self, framekey, nframes, blocksize):
        assert isinstance(nframes, (int,type(None)))
        assert isinstance(blocksize, (int,type(None)))

        iterblocks = None
        if blocksize is None:
            if nframes is None:
                # read to end in 1 block
                iterblocks = lambda: iter(self._readblocks(framekey))
            else:
                # read to nframes in 1 block
                iterblocks = lambda: iter([next(self._readblocks(framekey, blocksize=nframes))])

        else:
            if nframes is None:
                # read to end in blocks of size blocksize
                iterblocks = lambda: iter(self._readblocks(framekey, blocksize=blocksize))
            else:
                # read to nframes in blocks of size blocksize
                nblocks = bool(nframes%blocksize) + (nframes // blocksize)
                if nframes % blocksize:
                    nframes %= blocksize
                else:
                    nframes = blocksize

                print(nblocks, blocksize, nframes)
                iterblocks = lambda: chain.from_iterable(
                  iter([next(self._readblocks(framekey, blocksize=blocksize))
                        for i in range(nblocks-1)]\
                  +[next(self._readblocks(framekey, blocksize=nframes))])
                )

        return iterblocks

    def __iter__(self):
        # TODO implement via blockReadIterator
        raise NotImplementedError

    
