
import numpy as np

from .features import nofeature, distance, angle, dihedral, feature


class Featurizer(object):
    '''Class that applies feature calculations to trajectory data
    Pass the data on initialization, then add and apply feature
    calculations to build a feature trajectory.

    Attributes
    ----------
    trajectory

    Methods
    -------
    add_features
    featurize
    '''
    # TODO cls._available_features
    _nofeature_ = nofeature
    _distance_ = distance
    _angle_ = angle
    _dihedral_ = dihedral

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
            # TODO use featurelabels
            # featurelabel = featurename + '-' + \
            #        '_'.join([str(ai) for ai in atom_indices])
            if hasattr(self, featurefunc):
                ff = lambda: getattr(self, featurefunc)(
                    self._trajectory_coords, atom_indices)

            # elif isinmodule: bind_from_module
            elif callable(featurefunc):
                ff = lambda: feature(
                    featurefunc, self._trajectory_coords, atom_indices)

            else:
                raise Warning(
                    "Feature '{}' not added, require callable or "
                    "existing feature name".format(featurename))

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
    def trajectory(self):
        '''Get the trajectory of all features calculated so far
        '''
        return self._trajectory
