
import numpy as np

from features import nofeature, dihedral, angle, distance


class Featurizer(object):
    '''Class that applies feature calculations to trajectory data
    Pass the data on initialization, then add and apply feature calculations
    to build a feature trajectory.

    Attributes
    ----------
    trajectory

    Methods
    -------
    add_features
    featurize
    '''
    #_features = 
    _dihedral_ = dihedral
    _nofeature_ = nofeature
    _angle_ = angle
    _distance_ = distance

    def __init__(self, trajectory=None):
        super(Featurizer, self).__init__()

        self._trajectory_coords = trajectory
        self._feature_buffer = list()
        self._trajectory = None

    def add_features(self, features):
        '''Add a group of features to be calculated
        with a call to `featurize`
        '''
        while features:
            featurename, atom_indices = features.pop()
            featurefunc = '_{}_'.format(featurename)
            featurelabel = featurename + '-' + '_'.join([str(ai) for ai in atom_indices])
            if hasattr(self, featurefunc):
                ff = lambda: getattr(self, featurefunc)(self._trajectory_coords, atom_indices)

            #elif isinmodule: bind_from_module
            elif callable(featurefunc):
                ff = lambda: _feature(featurefunc, self._trajectory_coords, atom_indices)

            else:
                raise Warning("Feature '{}' not added, require callable or name of existing feature function".format(featurename))

            self._feature_buffer.append(ff)

    def featurize(self):
        '''Perform the pending featurize operations
        '''
        featuretrajs = list()
        while self._feature_buffer:
            # Append results of feature-trajectory-returning functions
            featuretrajs.append(self._feature_buffer.pop(0)())

        vs = [featuretrajs]
        if self.trajectory:
            vs.prepend(self.trajectory) 

        self._trajectory = np.vstack(vs)


    @property
    def trajectory
        '''Get the trajectory of all features calculated so far
        '''
        return self._trajectory



def featurizer(corefunc):
    '''Decorator to create feature trajectory
    from atom coordinate trajectory array given to the
    parent function. Create a featurizer function by
    passing the atoms-to-feature calculation to the
    featurizer decorator

    Usage
    -----
     ```
     @featurizer(calculate_dihedral_from_4atoms)
     def dihedral(trajectory_4atoms):
         return trajectory_4atoms
     ```
    '''
    def _flatten_atomcoords(trajectory_array):
        '''Preprocessing function to flatten coordinates
        fed to featurizer wrapper. Allows apply_along_axis function
        to create feature trajectory from atom coordinate array.
        '''
        nframes, natoms, ncoords = trajectory_array.shape
        assert ncoords == 3

        return trajectory_array.reshape(nframes, natoms*ncoords)


    def _featurizer(featurefunc):
        def wrapper(array, *args, **kwargs):

            assert isinstance(array, np.ndarray)
            featurized = np.apply_along_axis(
              corefunc, 1, _flatten_atomcoords(featurefunc(array, *args, **kwargs))
            )
            return featurized
        return wrapper

    return _featurizer


def _feature(calculation_on_atomcoords, trajectory_array, atom_indices=None):

    @featurizer(calculation_on_atomcoords)
    def _trajectory(trajectory_array, atom_indices=None):
        if atom_indices:
            return trajectory_array[:,atom_indices,:]
        else:
            return trajectory_array
    
    return lambda: _trajectory(trajectory_array, atom_indices)

