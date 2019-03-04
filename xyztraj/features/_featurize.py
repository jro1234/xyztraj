
import numpy as np


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

    def _featurizer(featurefunc):
        def wrapper(array, *args, **kwargs):

            assert isinstance(array, np.ndarray)
            featurized = np.apply_along_axis(
                corefunc, 1, _flatten_atomcoords(
                    featurefunc(array, *args, **kwargs))
            )
            return featurized

        return wrapper

    return _featurizer


def _feature(calculation_on_atomcoords, trajectory_array,
             atom_indices=None):

    @featurizer(calculation_on_atomcoords)
    def _trajectory(trajectory_array, atom_indices=None):
        if atom_indices:
            return trajectory_array[:, atom_indices, :]

        else:
            return trajectory_array

    return lambda: _trajectory(trajectory_array, atom_indices)
