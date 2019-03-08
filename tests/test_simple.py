#!/usr/bin/env python

import os

import xyztraj


reader = xyztraj.XYZReader()

class TestClass(object):
    # FIXME this line should work
    #self.traj = reader.readfile('tests/data/rnatraj.xyz')
    traj = reader.readfile('tests/data/rnatraj.xyz', nframes=1000)
    traj_len_answer = 100

    def test_trajlength(self):
        assert self.traj.trajectory.shape[0] == self.traj_len_answer
