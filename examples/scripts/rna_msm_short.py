#!/usr/bin/env python

import os

import numpy as np
import pyemma.coordinates as coor
import pyemma.msm as mm

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import pyemma.plots as pymplt
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatter 

from xyztraj import XYZReader
from xyztraj.features import (
  dihedral, nofeature, distance, angle
)

# TODO colormap setup
cm_reds = plt.get_cmap('Reds')


## Put all plot paths in `plotdir`
## to make sure they can be made
#_plotdir = lambda d: os.path.join("plots/4shorttrajs", d)
#datadir = '../data'
#
#def plotdir(d=''):
#    assert isinstance(d, str)
#    try:
#        os.makedirs(_plotdir(
#          os.path.directory(d),
#        ))
#    except FileExistsError:
#        pass
#
#plotdir()


plotdir = lambda d: os.path.join("plots/4shorttrajs", d)
datadir = '../data'
try:
    os.makedirs(plotdir(''))
except FileExistsError:
    pass

#=======================================#
# Step 1: Where are my Trajectory Files #
#=======================================#
xyzfiles = [os.path.join(datadir, fnm) for fnm in
 filter(lambda fn: fn.startswith('sim'), os.listdir(datadir))]

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

# Each Alone
for i in range(len(tj_chi)):
    plt.scatter(tj_chi[i], tj_ONdist[i], c=range(len(tj_chi[i])), cmap='nipy_spectral', s=0.5)
    finalize_chi_vs_ONdist(i)

# All Together
for i in range(len(tj_chi)):
    plt.scatter(tj_chi[i], tj_ONdist[i], c=range(len(tj_chi[i])), cmap='nipy_spectral', s=0.5)

finalize_chi_vs_ONdist()

#=======================================#
# Step 6: MSM Analyses                  #
#=======================================#
# Doing MSM Analysis
# tica of feature trajectories
lags = [5, 10, 25, 50, 100, 150, 300]
for lag in lags:
    try:
        os.makedirs(plotdir('tica-{}'.format(lag)))
    except FileExistsError:
        pass

ticas = list()
[ticas.append(coor.tica(tj_features, lag=lag)) for lag in lags]

#FIXME this bad if large trajs
#FIXME only works if single traj tica objects
ttrajs = [tica.get_output([0,1])[0] for tica in ticas]

# clustering with default k
ks = [5, 10, 25, 50] # TODO optimize clustering
clusts = list()
[clusts.append(coor.cluster_kmeans(tica, max_iter=40)) for tica in ticas]

# TICA Trajectories
for i,ttraj in enumerate(ttrajs):
    plt.scatter(*ttraj.T, c=range(ttraj.shape[0]), cmap='nipy_spectral', s=0.5)
    cb = plt.colorbar()
    plt.savefig(plotdir('tica-{}/tica-traj.png'.format(ticas[i].lag)))
    plt.close()

# TICA Landscapes
for i,tica in enumerate(ticas):
    pymplt.plot_free_energy(*tica.get_output([0,1])[0].T)
    #plt.scatter(clusts[i].clustercenters[:,:2], 
    plt.savefig(plotdir('tica-{}/tica-cc-landscape.png'.format(tica.lag)))
    plt.close()

# making MSMs for each lag
its = list()
for i,clust in enumerate(clusts):
    its.append(mm.its(clust.dtrajs, lags=lags, errors='bayes'))
    pymplt.plot_implied_timescales(its[-1])
    plt.savefig(plotdir('tica-{0}/timescales.png'.format(ticas[i].lag)))
    plt.close()

# # # Chapman-Kolmogorov tests
# # nstates = [2,3,4,5]
# # for i,itsb in enumerate(its):
# #     for msm in itsb.models:
# #         for ns in nstates:
# #             cktest = msm.cktest(ns)
# #             pymplt.plot_cktest(cktest)
# #             plt.savefig(plotdir("tica-{0}/cktest-{1}_lag-{2}_state.png".format(ticas[i].lag, msm.lag, ns)))
# #             plt.close()

#=======================================#
# Step 7: Analyses Plotting             #
#=======================================#
def invcount_sampling_distribution(binned_counts):
    sampling_probabilities = 1/binned_counts
    sampling_probabilities[sampling_probabilities==np.inf] = 0
    sampling_probabilities /= np.sum(sampling_probabilities)
    return sampling_probabilities
    

#for i,tica in enumerate(ticas):
#    for nbin in nbins: plot_as_density(tica.get_output([0,1])[0], nbin, "{}-tica".format(i))
#

# TODO separate functionality
def plot_as_density(featuretraj, nbins, ntraj='', nsamples=5, selectionmethod='weights'):
    '''Use 'weights' or 'ranks' as selection method
    '''
    binned, xbinedges, ybinedges = np.histogram2d(*featuretraj.T, bins=nbins)
    ## TODO understand why the datashape inversion is necessary...
    binned = np.flip(binned.T, axis=0)
    # small addition to prevent max observed value in each dimension from
    # matching edge value and being in its own bin outside the final desired bin
    xbinedges[-1] += 0.000000001
    ybinedges[-1] += 0.000000001
    sampling_probabilities = invcount_sampling_distribution(binned)
    xlims = xbinedges[0::xbinedges.shape[0]-1]
    ylims = ybinedges[0::ybinedges.shape[0]-1]
    # Density Plot ==================================================#
    plt.imshow(binned, extent=np.concatenate([xlims,ylims]), aspect='auto')
    cb = plt.colorbar()
    cb.set_label("Bin Counts")
    plt.savefig(plotdir('2dhist_{0}-{1}-2feat-count.png'.format(ntraj,nbins)), dpi=250)
    plt.close()
    # AS Plot =======================================================#
    logfsp = np.log(sampling_probabilities)
    logfsp[np.isneginf(logfsp)] = -9
    plt.imshow(logfsp, extent=np.concatenate([xlims,ylims]), aspect='auto', )#cmap='inferno')#, vmax=0.018)
    formatter = LogFormatter(10, labelOnlyBase=False)
    tickrange = logfsp.max() - logfsp.min()
    ncbticks = 6.
    ticks = [i/ncbticks*tickrange + tickrange/ncbticks/2. + logfsp.min() for i in range(int(ncbticks))]
    cb = plt.colorbar(ticks=ticks)#ticks=[float(i)/5* for i in range(5)], format=formatter)
    cb.set_ticklabels(['{:.4f}'.format(np.exp(t)) for t in ticks])
    cb.set_label("Sampling probability")
    plt.savefig(plotdir('AS-2dhist_{0}-{1}-2feat-invcount.png'.format(ntraj,nbins)), dpi=250)
    plt.close()
    # Make sampling selections ======================================#
    tbins = nbins**2
    sampledbins = np.zeros(binned.shape, dtype=int)
    if selectionmethod='weights':
        samplefunc = lambda: np.random.choice(
          range(tbins), size=nsamples, p=sampling_probabilities.flat, replace=False,)
    elif selectionmethod = 'ranks':
        samplefunc = lambda: sampling_probabilities.flat[list(reversed(np.argsort(sampling_probabilities.flat)))[:nsamples]]
    for bidx in samplefunc():
        sampledbins[(bidx//nbins, bidx%nbins)] += 1
    print(sampling_probabilities)
    print(sampledbins)
    # Plot with boxes around selected bins ==========================#
    sampled_ybins, sampled_xbins = np.argwhere(sampledbins).T
    # may not be same as nsamples if states sampled multiple times
    nsampledstates = len(sampled_ybins)
    xedges = xbinedges[np.hstack([sampled_xbins,sampled_xbins+1])]
    yedges = ybinedges[::-1][np.hstack([sampled_ybins,sampled_ybins+1])]
    print('sampled xbins=', sampled_xbins)
    print('sampled ybins=', sampled_ybins)
    print('xedges=', xedges)
    print('yedges=', yedges)
    logfsp = np.log(sampling_probabilities)
    logfsp[np.isneginf(logfsp)] = -9
    #sampling_probabilities[sampling_probabilities==0] = 0.00000001
    #plt.imshow(sampling_probabilities, extent=np.concatenate([xlims,ylims]), norm=LogNorm(), aspect='auto', )#cmap='inferno')#, vmax=0.018)
    plt.imshow(logfsp, extent=np.concatenate([xlims,ylims]), aspect='auto', )#cmap='inferno')#, vmax=0.018)
    formatter = LogFormatter(10, labelOnlyBase=False)
    tickrange = logfsp.max() - logfsp.min()
    ncbticks = 6.
    ticks = [i/ncbticks*tickrange + tickrange/ncbticks/2. + logfsp.min() for i in range(int(ncbticks))]
    cb = plt.colorbar(ticks=ticks)#ticks=[float(i)/5* for i in range(5)], format=formatter)
    cb.set_ticklabels(['{:.4f}'.format(np.exp(t)) for t in ticks])
    cb.set_label("Sampling probability")
    # TODO TODO the boxes as line plots using bin edges
    [[
      plt.plot(
        (xedges[s],xedges[s]),
        yedges[s::nsampledstates],
        c='red', lw=2,
        #c=cm(5*sampling_probabilities[sampled_xbins[s],sampled_ybins[s]]),
        label='{}'.format(sampling_probabilities[sampled_xbins[s],sampled_ybins[s]]),
      ),
      plt.plot(
        (xedges[s+nsampledstates],xedges[s+nsampledstates]),
        yedges[s::nsampledstates],
        c='red', lw=2,
        #c=cm(5*sampling_probabilities[sampled_xbins[s],sampled_ybins[s]]),
      ),
      plt.plot(
        xedges[s::nsampledstates],
        (yedges[s+nsampledstates],yedges[s+nsampledstates]),
        c='red', lw=2,
        #c=cm(5*sampling_probabilities[sampled_xbins[s],sampled_ybins[s]]),
      ),
      plt.plot(
        xedges[s::nsampledstates],
        (yedges[s],yedges[s]),
        c='red', lw=2,
        #c=cm(5*sampling_probabilities[sampled_xbins[s],sampled_ybins[s]]),
      ),
      ]
      for s in range(nsampledstates)
    ]
    # Get frames in bin =============================================#
    xbins = np.digitize(featuretraj[:,0], xbinedges) - 1
    ybins = np.digitize(featuretraj[:,1], ybinedges[::-1]) - 1
    binnes = np.array([xbins,ybins])
    print(ybins)
    print(featuretraj[:,1])
    print(ybinedges)
    binnedframes = dict()
    for xbin,ybin in zip(sampled_xbins, sampled_ybins):
        xbin_frames = np.argwhere(xbins==xbin).squeeze()#reshape(xbin_frames.shape[0])
        ybin_frames = np.argwhere(ybins==ybin).squeeze()#reshape(ybin_frames.shape[0])
        binnedframes[(ybin, xbin)] = sharedframes = np.intersect1d(xbin_frames, ybin_frames)
        plt.scatter(*featuretraj[sharedframes].T, s=1.75, c='pink', zorder=30)
    # Use to compare against original histogram
    countmatrix = np.zeros(sampledbins.shape)
    for k,v in binnedframes.items():
        countmatrix[k] = len(v)
    # Asserts same number of frames found by just-finished
    # sampled bins counting that histogram2d found at beginning
    assert all([
      binned[tuple(loc)] == countmatrix[tuple(loc)]
      for loc in np.argwhere(countmatrix)
    ])
    print('-'.join(['']*100))
    print(binned)
    print('-'.join(['']*100))
    print(countmatrix)
    print('-'.join(['']*100))
    sampledframes = dict()
    for k,v in binnedframes.items():
        # FIXME no-replace will break when sampling more times than there are observations
        sampledframes[k] = np.random.choice(v, size=sampledbins[k], replace=False)
    for f in sampledframes.values():
        plt.scatter(*featuretraj[f].T, s=0.25, c='green', zorder=35)
    plt.savefig(plotdir('AS-sampled-2dhist_{0}-{1}-2feat-invcount.png'.format(ntraj,nbins)), dpi=600)
    plt.close()
    return sampledframes, sampledbins, binnedframes

sampledframes, sampledbins, binnedframes = plot_as_density(np.concatenate(tj_features), 30, 'all', 10, 'ranks')

# Select frame from each selected bin
print("sampledframes=",sampledframes)

from pprint import pformat
with open(plotdir('sampled_frames.txt'), 'w') as f:
    f.write(pformat(sampledframes))

sampled_frames_2Dindex = dict()
totaltjlength = [sum([len(tjf) for tjf in tj_features[:i]])
                 for i in range(1 + len(tj_features))]

for k,v in sampledframes.items():
    whichtraj = np.max(np.argwhere(v > totaltjlength))
    sampled_frames_2Dindex[k] = (whichtraj, int(v - totaltjlength[whichtraj]))

with open(plotdir('sampled_frames_2Didx.txt'), 'w') as f:
    f.write(pformat(sampled_frames_2Dindex))


