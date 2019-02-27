#!/usr/bin/env python

import numpy as np
import pyemma.coordinates as coor

from featurize import dihedral
from xyzparser import XYZReader

xyzfile = '../data/sim1_pos_all.xyz'

r = XYZReader()
tj = r.readfile(xyzfile, nframes=10000)

# We have to pre-featurize the trajectory when giving
# pyemma arrays instead of recognized trajectory files
chi_torsion_atoms = (0, 3, 13, 18)
tj_chi = dihedral(tj.trajectory[:, chi_torsion_atoms, :])


#coor.source(tj.trajectory)
