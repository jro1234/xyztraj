#!/usr/bin/env python

import numpy as np
import pyemma.coordinates as coor
import pyemma.msm as mm

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import pyemma.plots as pymplt

from xyztraj import XYZReader
from xyztraj.features import (
  dihedral, nofeature, distance, angle
)

xyzfile = '../data/sim1_pos_all.xyz'

r = XYZReader()
traj = r.readfile(xyzfile, nframes=10000)
tj = traj.trajectory

# We have to pre-featurize the trajectory when giving
# pyemma arrays instead of recognized trajectory files
chi_torsion_atoms = (0, 3, 13, 18)
nh_atoms = (18, 9)
on_atoms = (8, 18)
onh_atoms = (8, 18, 9)

tj_chi = dihedral(tj, chi_torsion_atoms)
tj_NHdist = distance(tj, nh_atoms)
tj_ONdist = distance(tj, on_atoms)
tj_ONHangle = angle(tj, onh_atoms)
tj_01 = nofeature(tj, [0,1])
tj_01dist = distance(tj, [0,1])

tj_features = np.array([
  tj_chi, tj_ONdist, tj_ONHangle, #tj_NHdist, 
]).T

# tica of feature trajectory
tica = coor.tica(tj_features, lag=150)
# clustering with default k
clust = coor.cluster_kmeans(tica, max_iter=40)

# making MSMs for each lag
lags = [5, 10, 25, 50, 100, 150, 300]
its = mm.its(clust.dtrajs, lags=lags, errors='bayes')
pymplt.plot_implied_timescales(its)
plt.savefig('timescales.png')
plt.close()

nstates = [2,3,4]
for msm in its.models:
    for ns in nstates:
        cktest = msm.cktest(ns)
        pymplt.plot_cktest(cktest)
        plt.savefig("msm-{0}_lag-{1}_state.png".format(msm.lag, ns))
        plt.close()

pymplt.plot_free_energy(*tica.get_output([0,1])[0].T)
plt.savefig('tica-landscape.png')
plt.close()

