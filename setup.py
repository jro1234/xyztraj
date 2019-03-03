
from setuptools import setup
import versioneer

setup(
    name='xyztraj',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=['xyztraj'],#'reader','trajectory'],
    license='GNU',
    #long_description=open('README.txt').read(),
)
