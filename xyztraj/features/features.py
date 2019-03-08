
import numpy as np

# Nice name for each feature, users should import from
# here to make features in their own scripts
from ._featurize import _feature as feature



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


def angle(trajectory_array, atom_indices=None):
    return feature(_angle, trajectory_array, atom_indices)()


@n_points(3)
def _angle(points):
    '''Order is important
    '''
    p0, p1, p2 = points

    return np.degrees(np.arccos(
        np.dot(p1 - p0, p2 - p1) / \
        np.linalg.norm(p0 - p1) /  \
        np.linalg.norm(p2 - p1)
    ))


def nofeature(trajectory_array, atom_indices=None):
    return feature(lambda x: x, trajectory_array, atom_indices)()


def dihedral(trajectory_array, atom_indices=None):
    '''Calculate the dihedral angle trajectory for a set of atoms
    Returns
    -------
    feature_trajectory :: numpy array (mxd)
    Trajectory array of m frames each with d-dimensional feature value
    '''
    # TODO do type check/asserts in here?
    #       - yes, fail early
    #       - no, more flexible?
    return feature(_dihedral, trajectory_array, atom_indices)()


def distance(trajectory_array, atom_indices=None):
    '''Array of 3D norms of timeseries of 2 points
    '''
    # Not doing this way, faster implementation is easy
    # return feature(_distance, trajectory_array, atom_indices)()
    assert trajectory_array.shape[2] == 3

    if atom_indices is None:
        assert trajectory_array.shape[1] == 2
        atom_indices = [0, 1]

    a1, a2 = [trajectory_array[:, ai, :] for ai in atom_indices]

    return np.linalg.norm(a1 - a2, axis=1)


@n_points(4)
def _dihedral(points):
    '''Praxeolitic formula
    Arguments
    ---------
    points :: numpy array (4x3) or numpy array (12)
    4 points in cartesian 3D space
    Returns
    -------
    Dihedral from 1 sqrt, 1 cross product
    from :: https://stackoverflow.com/questions/20305272/dihedral-torsion-angle-from-four-points-in-cartesian-coordinates-in-python  # noqa E501
    '''
    p0, p1, p2, p3 = points

    b0 = -1.0 * (p1 - p0)
    b1 = p2 - p1
    b2 = p3 - p2

    # normalize b1 so that it does not influence magnitude of vector
    # rejections that come next
    b1 /= np.linalg.norm(b1)

    # vector rejections
    # v = projection of b0 onto plane perpendicular to b1
    #   = b0 minus component that aligns with b1
    # w = projection of b2 onto plane perpendicular to b1
    #   = b2 minus component that aligns with b1
    v = b0 - np.dot(b0, b1) * b1
    w = b2 - np.dot(b2, b1) * b1

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.dot(v, w)
    y = np.dot(np.cross(b1, v), w)

    # FIXME not a robust method to unwrap
    angle = np.degrees(np.arctan2(y, x))

    return angle if angle > 0 else 360 + angle
