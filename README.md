
This package is for reading xyz trajectories in python. There are
currently 2 main objects, a `XYZReader` that gets the data from a
file, and a `XYZTrajectory` object that this reader creates and
returns. 

You can clone and install this repository with
```bash
git clone https://github.com/jrossyra/xyzparser
cd xyzparser
python setup.py install
```

To read an xyz trajectory file, use it like this:
```python
from xyzparser import XYZReader
reader = XYZParser()
traj = reader.readfile('mytraj.xyz')
```

**NotYetButvvSoon**
The reader can be used repeatedly to read in differently formatted
trajectories. Each `XYZTrajectory` instance will be constructed by
the reader to fill in the necessary fields for writing, so there
is no writer class but rather a save capability on the trajectory.
You can use atom slices and trajectory strides to subsample a
trajectory this way for further processing.
