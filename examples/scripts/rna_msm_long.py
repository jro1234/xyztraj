#!/usr/bin/env python

import os

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

plotdir = lambda d: os.path.join("plots/longtraj", d)
datadir = '../data/Sedova_Ossyra_AIMD_AMD'

try:
    os.makedirs(plotdir(''))
except FileExistsError:
    pass

#=======================================#
# Step 1: Where are my Trajectory Files #
#=======================================#
xyzfiles = [os.path.join(datadir, fnm) for fnm in os.listdir(datadir)]

#=======================================#
# Step 2: Read the Trajectory Files     #
#=======================================#
r = XYZReader()
trajs = list()
for xyzfile in xyzfiles:
    traj = r.readfile(xyzfile, nframes=10000)
    trajs.append(traj.trajectory)

#=======================================#
# Step 3: Define Atom Sets for Features #
#=======================================#
# We have to pre-featurize the trajectory when giving
# pyemma arrays instead of recognized trajectory files
chi_torsion_atoms = (0, 3, 13, 18)
nh_atoms = (18, 9)
on_atoms = (8, 18)
onh_atoms = (8, 18, 9)

#=======================================#
# Step 4: Calculate Features            #
#=======================================#
tj_chi = [dihedral(tj, chi_torsion_atoms) for tj in trajs]
tj_NHdist = [distance(tj, nh_atoms) for tj in trajs]
tj_ONdist = [distance(tj, on_atoms) for tj in trajs]
tj_ONHangle = [angle(tj, onh_atoms) for tj in trajs]
#tj_01 = nofeature(tj, [0,1])
#tj_01dist = distance(tj, [0,1])

#=======================================#
# Step 5: Plot Feature Trajectories     #
#=======================================#
# 1-D Feature Plot
tj_features = [np.array([
  tj_chi[i], tj_ONdist[i], #tj_ONHangle[i], #tj_NHdist[i], 
]).T for i in range(len(trajs))]
plt.plot(tj_chi[0])
plt.suptitle("Chi angle for Trajectory 1")
plt.savefig(plotdir("chi_traj_1.png"))
plt.close()

# Feature Space Trajectories
#  - O-N distance vs. Chi Torsion Angle
def finalize_chi_vs_ONdist(nametag=''):
    if str(nametag):
        nametag = '-' + str(nametag)
    cb = plt.colorbar()
    cb.set_label("MD Step Number")
    plt.xlabel("Chi Angle of Atoms [$^\circ$]")
    plt.ylabel("O-N Atomic Distance [$\AA$]")
    plt.suptitle("Feature Trajectory")
    plt.savefig(plotdir("trajs-tica{}.png".format(nametag)), dpi=600)
    plt.close()

# Each traj Alone
for i in range(len(tj_chi)):
    plt.scatter(tj_chi[i], tj_ONdist[i], c=range(len(tj_chi[i])), s=0.5)
    finalize_chi_vs_ONdist(i)

for i in range(len(tj_chi)):
    plt.scatter(tj_chi[i], tj_ONdist[i], c=range(len(tj_chi[i])), s=0.5)

finalize_chi_vs_ONdist()

#=======================================#
# Step 6: MSM Analyses                  #
#=======================================#
# Doing MSM Analysis
# tica of feature trajectories
lags = [5, 10, 25, 50, 100, 150, 300]
for lag in lags:
    os.makedirs(plotdir('tica-{}'.format(lag)))

ticas = list()
[ticas.append(coor.tica(tj_features, lag=lag)) for lag in lags]

# clustering with default k
ks = [5, 10, 25, 50] # TODO optimize clustering
clusts = list()
[clusts.append(coor.cluster_kmeans(tica, max_iter=40)) for tica in ticas]

# TICA Landscapes
for i,tica in enumerate(ticas):
    try:
    pymplt.plot_free_energy(*tica.get_output([0,1])[0].T)
    #plt.scatter(clusts[i].clustercenters[:,:2], 
    plt.savefig(plotdir('tica-{}/tica-cc-landscape.png'.format(tica.lag)))
    plt.close()
    except 

# making MSMs for each lag
its = list()
for i,clust in enumerate(clusts):
    its.append(mm.its(clust.dtrajs, lags=lags, errors='bayes'))
    pymplt.plot_implied_timescales(its[-1])
    plt.savefig(plotdir('tica-{0}/timescales.png'.format(ticas[i].lag)))
    plt.close()

# Chapman-Kolmogorov tests
nstates = [2,3,4,5]
for i,itsb in enumerate(its):
    for msm in itsb.models:
        for ns in nstates:
            cktest = msm.cktest(ns)
            pymplt.plot_cktest(cktest)
            plt.savefig(plotdir("tica-{0}/cktest-{1}_lag-{2}_state.png".format(ticas[i].lag, msm.lag, ns)))
            plt.close()

#for i,itsb in 

