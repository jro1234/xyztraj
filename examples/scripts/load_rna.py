from xyzparser import XYZReader

xyzfile = '../../examples/data/sim1_pos_all.xyz'
r = XYZReader()

print("Should have 3 frames in 1 block")
tj1 = r.readfile(xyzfile, nframes=3)

print("Should have 2 frames in 1 block twice then 1 frames in 1 block")
tj2 = r.readfile(xyzfile, blocksize=2, nframes=5)

print("Should have 3 frames in 1 block")
tj3 = r.readfile(xyzfile, blocksize=3, nframes=3)

print("Should have 3 frames in each of 3 blocks")
tj4 = r.readfile(xyzfile, blocksize=3, nframes=9)



