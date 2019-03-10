
import numpy as np


class n_points(object):
    '''Decorater to check that a group of n coorindates was given
    to feature-calculating function that uses n atom coordinates.
    Optionally, you can give an error message to the decorator to
    use in place of the default message.

    Decorated functions must take (nx3) array of 3D points as arg.

    Arguments
    ---------
    n :: int number of points this feature requires

    error_message [optional] ::  str message for incorrect input
        to the decorated function

    Example
    -------
    @n_points(4[, my_error])
    def my_feature_calculator(points):
        <body>
    '''
    _default_error = \
        "Could not format {n} points for feature function {func}"

    def __init__(self, n, error_message=None):
        assert isinstance(n, int)
        assert n > 0
        assert isinstance(error_message, (type(None), str))
        self.n = n
        self.n_coords_point = 3
        self.error_message = error_message

    def __call__(self, func):
        if self.error_message is None:
            self.error_message = self._default_error.format(
                func=func.__name__, n=self.n)

        def wrapper(points_array):
            '''Return point coordinate vectors
            '''
            if len(points_array.shape) == 2:
                assert points_array.shape[0] == self.n
                assert points_array.shape[1] == self.n_coords_point
                return func(points_array)

            elif len(points_array.shape) == 1:
                assert points_array.shape[0] == self.n_coords_point * self.n
                return func([  # sorting into (nx3) 2D array of n 3D points
                    points_array[i * self.n_coords_point:(i + 1) * self.n_coords_point]
                    for i in range(self.n)
                ])

            else:
                # hard to trigger, intermediate decorator shuffles array along
                raise ValueError(error_message)

        return wrapper


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

        return trajectory_array.reshape(nframes, natoms * ncoords)

    def _featurize(featurefunc):
        def wrapper(array, *args, **kwargs):

            assert isinstance(array, np.ndarray)
            return np.apply_along_axis(
                corefunc, 1,
                _flatten_atomcoords(
                    featurefunc(array, *args, **kwargs))
            )

        return wrapper

    return _featurize


def _feature(calculation_on_atomcoords, trajectory_array,
             atom_indices=None):

    @featurizer(calculation_on_atomcoords)
    def _trajectory(trajectory_array, atom_indices=None):
        if atom_indices:
            return trajectory_array[:, atom_indices, :]

        else:
            return trajectory_array

    return lambda: _trajectory(trajectory_array, atom_indices)
