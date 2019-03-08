
import numpy as np

# Nice name for each feature, users should import from
# here to make features in their own scripts
from ._featurize import _feature as feature


_default_points_error = \
    "Could not format {n} points for feature function {func}"


def n_points(n, error_message=None):
    '''Decorater to enforce format for group of n coorindates
    Wrap any feature-calculating function that uses atom
    coordinates to detect from a set of acceptible formats
    given n atoms.

    Example
    -------
    @n_points(4[, my_error])
    def my_feature_calculator(points):
        <body>
    '''
    n_coords_point = 3

    if error_message is None:
        error_message = error_message.format(func=func.__name__, n=n)

    def _wrapper(func):

        def wrapper(points_array):
            '''Return point coordinate vectors or raise error
            '''
            if len(points_array.shape) == 2:
                assert points_array.shape[1] == n_coords_point
                return func(points_array)

            elif points_array.shape[0] == n_coords_point * n:
                assert len(points_array.shape) == 1
                return func([
                    points_array[i * n_coords_point:(i + 1) * n_coords_point]
                    for i in range(n_coords_point)
                ])

            else:
                raise ValueError(error_message)

        return wrapper

    return _wrapper


def angle(trajectory_array, atom_indices=None):
    return feature(_angle, trajectory_array, atom_indices)()


@n_points(3, _default_points_error)
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


@n_points(4, _default_points_error)
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
