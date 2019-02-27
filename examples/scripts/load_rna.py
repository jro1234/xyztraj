from xyzparser import XYZReader

xyzfile = '../../examples/data/sim1_pos_all.xyz'
r = XYZReader()
print("Should have 3 frames in 1 block")
r.readfile(xyzfile, nframes=3)
print("Should have 3 frames in 1 block then 2 frames in 1 block")
r.readfile(xyzfile, blocksize=3, nframes=5)
print("Should have 3 frames in 1 block")
r.readfile(xyzfile, blocksize=3, nframes=3)
print("Should have 3 frames in each of 3 blocks")
r.readfile(xyzfile, blocksize=3, nframes=9)
