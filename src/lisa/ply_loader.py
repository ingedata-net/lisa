from plyfile import PlyData, PlyElement
from proto.input_pb2 import LidarDataFrame, LidarDataPoint
import numpy as np

def load(
  filename, frame,
  normalize_intensity=True,
  scale_intensity_factor=256
  ):
  plydata = PlyData.read(filename)

  xvalue = plydata['vertex']['x']
  yvalue = plydata['vertex']['y']
  zvalue = plydata['vertex']['z']
  ivalue = plydata['vertex']['intensity']

  if not isinstance(ivalue, np.ndarray):
    ivalue = plydata['vertex']['i']

  catch_intensity = isinstance(ivalue, np.ndarray)

  if catch_intensity:

    if normalize_intensity:
      max = np.amax(ivalue)
      ivalue = np.true_divide(ivalue, max)
    else:
      ivalue = np.multiply(ivalue, 1 / scale_intensity_factor)

    ivalue = np.clip(ivalue, 0, 255)

    for i in range(len(xvalue)):
      frame.points.add(x=xvalue[i], y=yvalue[i], z=zvalue[i], i=ivalue[i])

  else:
      frame.points.add(x=xvalue[i], y=yvalue[i], z=zvalue[i])

if __name__ == "__main__":
  frame = LidarDataFrame()
  load("sample/test.ply", frame)
  print(frame)
  pass