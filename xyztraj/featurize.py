
import numpy as np

def featurizer(corefunc):
    def _featurizer(featurefunc):
        def wrapper(array):
            assert isinstance(array, np.ndarray)
            featurized = np.apply_along_axis(corefunc, 0, array)
            return featurized
        return wrapper
    return _featurizer


def _dihedral(points):
    '''Praxeolitic formula
    Arguments
    ---------
    points :: numpy array (4x3)
    4 points in cartesian 3D space
    Returns
    -------
    Dihedral from 1 sqrt, 1 cross product
    from :: https://stackoverflow.com/questions/20305272/dihedral-torsion-angle-from-four-points-in-cartesian-coordinates-in-python
    '''
    p0 = points[0]
    p1 = points[1]
    p2 = points[2]
    p3 = points[3]

    b0 = -1.0*(p1 - p0)
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
    v = b0 - np.dot(b0, b1)*b1
    w = b2 - np.dot(b2, b1)*b1

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.dot(v, w)
    y = np.dot(np.cross(b1, v), w)

    return np.degrees(np.arctan2(y, x))


@featurizer(_dihedral)
def dihedral(p_array, dumb):
    return p_array

