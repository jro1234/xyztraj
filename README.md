[![Build Status](https://travis-ci.org/jrossyra/xyztraj.svg?branch=master)](https://travis-ci.org/jrossyra/xyztraj)
[![codecov.io](http://codecov.io/github/jrossyra/xyztraj/coverage.svg?branch=master)](http://codecov.io/github/jrossyra/xyztraj?branch=master)
XYZTraj is for reading xyz trajectories in Python, then preparing
the data for other Python-based trajectory analysis tools. We will call
this 'featurizing' the data, i.e. creating new trajectories by applying
a calculation to all the frames in the trajectory.

You can clone this repository and install the package with
```bash
git clone https://github.com/jrossyra/xyztraj
cd xyztraj
python setup.py install
```

There are
2 objects associated with retrieving data, an `XYZReader` that gets the data from a
file, and a `XYZTrajectory` object that this reader creates and
returns. Once you have the trajectory object, you can apply feature calculations with
the `Featurizer` object to create a new
trajectory in feature space.

Read an xyz trajectory file like this:
```python
from xyztraj import XYZReader

reader = XYZReader()
# An XYZTrajectory
traj = reader.readfile('mytraj.xyz')
# A numpy array of the coordinates
traj.trajectory
```

Then you can featurize your trajectory with calculations we provide or your own
simple (or complex) script that takes atomic coordinates to calculate something.
There are options for how to provide the featurizing function, here we just give
the name of functions in the `xyztraj.features` package. 
```python
from xyztraj.features import Featurizer

dihedral_atoms = [0,10,11,3]
keep_position_atoms = [2,4,6]
features = {'dihedral': dihedral_atoms, 'nofeature': keep_position_atoms}

featurizer = Featurizer(traj.trajectory)
featurizer.add_features(features)
featurizer.featurize()
featuretraj = featurizer.trajectory

# (mxd) shape of m frames by d feature dimensions
featuretraj.shape
```

The featurizing functions in `features`, or your functions,
can be given in place of the function name strings shown above.
Also, we can just keep featurizing the trajectory and append
to the featurespace.
```python
from xyztraj.features import distance

distance_atoms = [0,1]
featurizer.add_features({distance: distance_atoms})
featurizer.featurize()

# larger by the 1 feature dimension we just added
featuretraj.shape
```

We show the good practice of enforcing some input structure so
that you don't accidentally get a misunderstood result from
erroneous input that happens to calculte without error. The
coordinates are flattened, so make sure to take the number of
atoms indices given and multiply by 3.
```python
def calc_weirdfeature(atomcoordinates):
    # unknown frames is shape[0], 3xNatoms is shape[1]
    assert atomcoordinates.shape[1] == 12
    return np.mean(atomcoordinates)

weirdfeature_atoms = [13,11,15]
weirdfeature = {calc_weirdfeature: weirdfeature_atoms}

featurizer.add_features(weirdfeature)
featurizer.featurize()
featuretraj.shape
```

