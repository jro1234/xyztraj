from xyzparser import XYZReader

xyzfile = '../../examples/data/sim1_pos_all.xyz'
r = XYZReader()

tjA = r.readfile(xyzfile, nframes=10000)
if False:
    tjB = r.readfile(xyzfile, blocksize=100)#FIXME
    tjC = r.readfile(xyzfile, nframes=10000, blocksize=100)#FIXME
  
    print(tjA.trajectory.shape)
    print(tjB.trajectory.shape)
    print(tjC.trajectory.shape)
  
    print("Should have 3 frames in 1 block")
    tj1 = r.readfile(xyzfile, nframes=3)
    print(tj1.trajectory.shape)
  
    print("Should have 2 frames in 1 block twice then 1 frames in 1 block")
    tj2 = r.readfile(xyzfile, blocksize=2, nframes=5)
    print(tj2.trajectory.shape)
  
    print("Should have 3 frames in 1 block")
    tj3 = r.readfile(xyzfile, blocksize=3, nframes=3)
    print(tj3.trajectory.shape)
  
    print("Should have 3 frames in each of 3 blocks")
    tj4 = r.readfile(xyzfile, blocksize=3, nframes=9)
    print(tj4.trajectory.shape)


