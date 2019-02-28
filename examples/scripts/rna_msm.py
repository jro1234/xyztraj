#!/usr/bin/env python

import numpy as np
import pyemma.coordinates as coor

from xyztraj import XYZReader
from xyztraj.features import dihedral

xyzfile = '../data/sim1_pos_all.xyz'

r = XYZReader()
tj = r.readfile(xyzfile, nframes=10000)

# We have to pre-featurize the trajectory when giving
# pyemma arrays instead of recognized trajectory files
chi_torsion_atoms = (0, 3, 13, 18)
tj_chiatoms = tj.trajectory[:, chi_torsion_atoms, :]
nframes, natoms, ncoords = tj_chiatoms.shape

tj_chi = dihedral(tj_chiatoms)
print(tj_chi)


#coor.source(tj.trajectory)
