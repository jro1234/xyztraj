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
