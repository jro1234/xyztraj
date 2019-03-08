#!/usr/bin/env python

import os

import xyztraj


reader = xyztraj.XYZReader()

class TestClass(object):
    # FIXME this line should work
    #self.traj = reader.readfile('tests/data/rnatraj.xyz')
    traj = reader.readfile('tests/data/rnatraj.xyz', nframes=1000)
    trajdims_answer = [100, 632, 3]

    def test_trajdims(self):
        assert self.traj.trajectory.shape[0] == self.traj_len_answer

    def test_dihedral(self):
        chi_atoms = (0, 3, 13, 18)
        traj_chi = xyztraj.features.dihedral(
            self.traj.trajectory, chi_atoms)
        assert traj_chi.shape == (self.trajdims_answer[0], 1)
