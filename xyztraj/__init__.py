
from .reader import XYZReader
from .trajectory import XYZTrajectory

from . import features


from ._version import get_versions
__version__ = get_versions()['version']
version     = __version__
del get_versions


