#!/usr/bin/env python

import os

import xyztraj


reader = xyztraj.XYZReader()
posbox = 'tests/data/box.xyz'
posbox_shape = [6, 8, 3]
tolerance = 0.0001

class TestClass(object):

    # FIXME this line should work
    #self.traj = reader.readfile('tests/data/rnatraj.xyz')
    traj = reader.readfile(posbox, nframes=1000)
    trajdims_answer = posbox_shape

    def test_trajdims(self):

        assert self.traj.trajectory.shape[0] == self.trajdims_answer[0]

    def test_dihedral(self):

        chi_atoms = (0, 1, 2, 3)
        traj_chi = xyztraj.features.dihedral(
            self.traj.trajectory, chi_atoms)

        assert len(list(filter(lambda _s: _s != 1, traj_chi.shape))) == 1
        assert traj_chi.shape[0] == self.trajdims_answer[0]
        assert all([tjc - 90 < tolerance for tjc in traj_chi])

    def test_cutoffcorners(self):

        atoms_close = [[0,1], [0,2], [0,3], [1,6], [1,5], [2,4],
                       [2,6], [3,4], [3,5], [4,7], [5,7], [6,7]]
        dist_atoms_close = 1.
        atoms_far = [[0,4], [0,5], [0,6], [0,7], [4,1], [4,5], [4,6]]
        super_far = [False, False, False, True, True, False, False]
        dists_atoms_far = [xyztraj.features.distance(
            self.traj.trajectory, ap) for ap in atoms_far]

        cutoff_closeones = []
        cutoff_farones = []

        for atompair in atoms_close:
            cutoff_closeones.append(
                xyztraj.features.contact(self.traj.trajectory, atompair, 1.01)
            )

        assert all([all(cc) for cc in cutoff_closeones])

        for atompair in atoms_far:
            cutoff_farones.append(
                xyztraj.features.contact(self.traj.trajectory, atompair, 1.42)
            )

        assert all([all(cc) 
            for i,cc in enumerate(cutoff_farones) if not super_far[i]])
        assert all([all(cc==False)
            for i,cc in enumerate(cutoff_farones) if super_far[i]])
